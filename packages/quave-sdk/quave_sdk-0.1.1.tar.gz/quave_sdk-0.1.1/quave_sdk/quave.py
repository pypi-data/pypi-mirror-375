from __future__ import annotations
import requests
import warnings
import time
import asyncio
import getpass
from datetime import datetime, timezone
from typing import Any, Callable, Union, Optional
from supabase import create_client, Client, acreate_client, AClient, FunctionsError
from qiskit import QuantumCircuit
import numbers

from .job import Job, JobData, JobStatus
from .job_execution import JobExecution, JobExecutionData, JobExecutionStatus

JOB_TABLE = "jobs"
JOB_EXECUTION_TABLE = "job_executions"

class MultipleExecutionJob():
    override_job_id: Optional[str]
    reset_status: bool
    update_job_on_completion: bool

    def __init__ (self, override_job_id: Optional[str] = None, reset_status: bool = True, update_job_on_completion: bool = True):
        self.override_job_id = override_job_id
        self.reset_status = reset_status
        self.update_job_on_completion = update_job_on_completion

class Quave:
    """Client for interacting with the Quave quantum computing platform."""

    default_backend = "simulate"
    default_provider = "simulator"

    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        """
        Initializes the Quave client.

        Args:
            email (Optional[str]): User's email. If not provided, it will be prompted for interactively.
            password (Optional[str]): User's password. If not provided, it will be prompted for securely.
        """
        if not isinstance(email, str) or not email.strip():
            email = input("Enter your email: ").strip()

        if not isinstance(password, str) or not password.strip():
            password = getpass.getpass("Enter your password: ")
        
        self._supabase: Client = create_client("https://dykixucbxclbrwdvrgfx.supabase.co", "sb_publishable__zGmHDukGharhEpZd1NOgg_vpnZHnSx")
        response = self._supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        self._realtime: AClient = asyncio.run(acreate_client("https://dykixucbxclbrwdvrgfx.supabase.co", "sb_publishable__zGmHDukGharhEpZd1NOgg_vpnZHnSx"))
        a_response = asyncio.run(self._realtime.auth.sign_in_with_password({
            "email": email,
            "password": password
        }))

        self._base_url = "https://api.quave.qaion.com"

        if not response.session or not a_response:
            raise Exception("Authentication failed - invalid credentials")

    @staticmethod
    def _compile_to_ir(circuit: QuantumCircuit) -> str:
        """
        Transpile `circuit` and return an OpenQASM3 representation.
        
        Args:
            circuit (QuantumCircuit): quantum circuit to transpile to QASM3

        Returns:
            str: qasm3 string representation of the circuit
        """

        try:
            from qiskit import transpile, qasm3
        except Exception as exc:
            raise ImportError("qiskit is required for compiling circuits") from exc

        basis = ["u", "cx", "measure"]
        try:
            tcirc = transpile(circuit, basis_gates=basis, optimization_level=1)
        except Exception:
            tcirc = circuit
        
        return qasm3.dumps(tcirc)
    
    def _get_user_id(self) -> str:
        """
        Retrieves the user ID of the currently authenticated user.

        Returns:
            str: The user ID of the authenticated user.
        """
        return self._supabase.auth.get_user().user.id

    def _validate_supabase_session(self) -> None:
        """
        Automatically refreshes supabase session if expired.
        Call this before making Supabase API calls to ensure valid session
        """
        expiration_buffer = 60
        if self._supabase.auth.get_session().expires_at - expiration_buffer <= int(time.time()):
            refreshed = self._supabase.auth.refresh_session()
            if not refreshed or not refreshed.session:
                raise Exception("Session refresh failed. Please log in again.")
        
    async def _validate_realtime_session(self) -> None:
        """
        Automatically refreshes supabase realtime session if expired.
        Call this before making Supabase realtime API calls to ensure valid session
        """
        expiration_buffer = 60
        session = await self._realtime.auth.get_session()
        if session.expires_at - expiration_buffer <= int(time.time()):
            refreshed = await self._realtime.auth.refresh_session()
            if not refreshed or not refreshed.session:
                raise Exception("Session refresh failed. Please log in again.")
            
    def _validate_parameters(self, circuit: QuantumCircuit, parameter_set: list[Optional[dict[str, float]]]) -> None:
        """
        Validates that the provided parameters match the circuit's parameters.

        Args:
            circuit (QuantumCircuit): The circuit to be executed
            parameter_set (list[Optional[dict[str, float]]]): A set of parameters in the circuit

        Raises:
            ValueError: If the number of parameters provided are not the same or some parameters are missing
        """
        circuit_params = circuit.parameters
        for parameters in parameter_set:
            if len(circuit_params) != len(parameters) or not all(param.name in parameters for param in circuit_params):
                raise ValueError(f"The number of parameters in the circuit ({len(circuit_params)}) was not equal to the number of parameters provided in {parameters}")
        
    def _validate_backend(self, backend: str) -> tuple[str, str]:
        """
        Validates that the provided backend is supported.

        Args:
            backend (str): The backend for the circuit to execute on

        Returns:
            tuple[str, str]: A tuple containing:
                - backend (str): Normalized backend name
                - provider (str): The provider associated with the backend

        Raises:
            Warning: If the backend is not supported
        """
        provider = Quave.default_provider
        if backend == Quave.default_backend:
            return backend, provider
        provider = None
        supported_backends = self.list_backends()
        if not supported_backends:
            warnings.warn("Failed to fetch supported backends so unable to validate backend", FutureWarning)
        else:
            for backend_provider, backend_list in supported_backends.items():
                if backend in backend_list:
                    provider = backend_provider
            if not provider:
                warnings.warn("Backend not supported. Defaulting to Aer simulator", FutureWarning)
                backend = Quave.default_backend
                provider = Quave.default_provider
        return backend, provider
    
    def _get_bearer_token(self) -> str:
        """
        Retrieves the current bearer token for authentication.

        Returns:
            str: The bearer token.
        """
        self._validate_supabase_session()
        return f"Bearer {self._supabase.auth.get_session().access_token}"
    
    def _execute_circuit(self, circuit: QuantumCircuit, parameters: Optional[Union[dict[str, float], list[dict[str, float]]]], shots: int, backend: str, multi_execution: Optional[MultipleExecutionJob] = None) -> tuple[JobData, list[JobExecutionData]]:
        """
        Queues circuit for execution with the specified backend and the assigned parameters.
        Facilitates single, batch, and iterative execution.

        Args:
            circuit (QuantumCircuit): The circuit to be executed
            parameters (Optional[Union[dict, list]]): The value of parameters in the circuit.
            shots (int): The number of shots for the circuit to execute
            backend (str): The backend for the circuit to execute on
            multi_execution (Optional[MultipleExecutionJob]): Object containing options for multi-execution jobs.

        Returns:
            tuple[JobData, list[JobExecutionData]]: A tuple containing the JobData and a list of JobExecutionData objects.
        
        Raises:
            RuntimeError: If Quave failed to queue the job.
            ValueError: If the number of parameters is incorrect.
            Exception: For other errors.
        """
        try:
            backend, provider = self._validate_backend(backend)
            if multi_execution and not isinstance(multi_execution, MultipleExecutionJob):
                raise TypeError("iterative_execution must be of type IterativeExecution")
            elif multi_execution and not isinstance(parameters, dict):
                raise ValueError("Jobs requiring multiple executions must submit parameters as a single dictionary for the current execution")
            
            self._validate_supabase_session()
            qasm = self._compile_to_ir(circuit)
            user_id = self._get_user_id()

            payload = {
                "qasm": qasm,
                "shots": shots,
                "backend": backend
            }

            expected_executions = 1

            if parameters:
                param_sets = parameters if isinstance(parameters, list) else [parameters]
                self._validate_parameters(circuit, param_sets)
                payload["parameters"] = param_sets
                expected_executions = len(param_sets)
            
            if multi_execution:
                payload["job_id"] = multi_execution.override_job_id
                payload["update_job"] = multi_execution.update_job_on_completion

            headers = {"Content-Type": "application/json", "Authorization": self._get_bearer_token()}
            url = f"{self._base_url}/v1/jobs"
            response = requests.post(url, headers=headers, json=payload)
            if not response.ok:
                error = None
                try:
                    error = response.json().get('error')
                except Exception:
                    if not error:
                        error = response.text
                raise RuntimeError(f"Failed to queue job: {error}")
            response.raise_for_status()
            queued_at = datetime.now(timezone.utc).isoformat()
            resp_json = response.json()

            if resp_json.get("status", "") != "accepted":
                raise RuntimeError(f"Failed to queue job: {resp_json.get('message', 'Unspecified error authenticating request')}")
            
            job_id = resp_json.get("job_id")
            execution_ids = resp_json.get("execution_ids")
            return_job, return_executions = None, []

            if not execution_ids:
                raise RuntimeError(f"Failed to stage job execution.")
            
            if len(execution_ids) < expected_executions:
                warnings.warn(f"Unable to parse all executions. Proceeding with {len(execution_ids)} executions", RuntimeWarning)

            job_data = {"id": job_id, "user_id": user_id, "status": "PENDING", "qasm": qasm}
            return_job = JobData(job_data)
            if not multi_execution or multi_execution.reset_status:
                self._supabase.table(JOB_TABLE).upsert(job_data).execute()
            
            rows = []
            for i in range(len(execution_ids)):
                execution_data = {
                    "id": execution_ids[i], 
                    "job_id": job_id, 
                    "status": "PENDING",
                    "shots": shots, 
                    "backend_name": backend, 
                    "provider": provider,
                    "queued_at": queued_at
                }
                if parameters:
                    execution_data["parameters"] = param_sets[i]

                rows.append(execution_data)
                return_executions.append(JobExecutionData(execution_data))

            self._supabase.table(JOB_EXECUTION_TABLE).insert(rows).execute()
            return return_job, return_executions
        except FunctionsError as e:
            raise Exception(f"Failed to store circuit execution: {e.message}") from e 
        except Exception as e:
            raise Exception(f"Failed to execute circuit: {str(e)}") from e # DEBUG - remove the str
        
    async def _await_job_completion(self, job: Job, timeout: float = 10000) -> Optional[JobData]:
        """
        Waits for a job to be complete and then returns JobData object asynchronously.

        Args:
            job (Job): The job to await completion for.
            timeout (float): Amount of seconds to wait before exiting.

        Returns:
            Optional[JobData]: Parsed row of the job if complete, otherwise None.
        """
        await self._validate_realtime_session()
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        def on_update(payload):
            new_data = payload.get("data")
            if new_data and new_data.get("record").get("id") == job.job_id:
                raw_data = new_data.get("record")
                job_data = JobData(raw_data)
                if job_data._cached_in_final_state() and not future.done():
                    future.set_result(job_data)

        channel = await self._realtime.channel("job_updates").on_postgres_changes(
            "UPDATE", schema="public", table=JOB_TABLE, filter=f"id=eq.{job.job_id}", callback=on_update
        ).subscribe()

        await asyncio.sleep(0.1)  # Allow some time for the subscription to be established

        try:
            current = self._get_job(job)
            if current and current._cached_in_final_state():
                if not future.done():
                    future.set_result(current)
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            warnings.warn(f"Timeout waiting for job {job.job_id}", RuntimeWarning)
            return None
        finally:
            await self._realtime.remove_channel(channel)

    async def _await_execution_completion(self, execution: JobExecution, timeout: float = 10000) -> Optional[JobExecutionData]:
        """
        Waits for an execution to be complete and then returns JobExecutionData object asynchronously.

        Args:
            execution (JobExecution): The execution to await completion for.
            timeout (float): Amount of seconds to wait before exiting.

        Returns:
            Optional[JobExecutionData]: Parsed row of the execution if complete, otherwise None.
        """
        await self._validate_realtime_session()
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        def on_update(payload):
            new_data = payload.get("data")
            if new_data and new_data.get("record").get("id") == execution.id:
                raw_data = new_data.get("record")
                execution_data = JobExecutionData(raw_data)
                if execution_data._cached_in_final_state() and not future.done():
                    future.set_result(execution_data)

        channel = await self._realtime.channel("execution_updates").on_postgres_changes(
            "UPDATE", schema="public", table=JOB_EXECUTION_TABLE, filter=f"id=eq.{execution.id}", callback=on_update
        ).subscribe()

        try:
            current = self._get_execution(execution)
            if current and current._cached_in_final_state():
                return current
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            warnings.warn(f"Timeout waiting for job execution {execution.id}", RuntimeWarning)
            return None
        finally:
            await self._realtime.remove_channel(channel)

    def _get_job(self, job: Job) -> JobData:
        """
        Retrieves the job metadata.

        Args:
            job (Job): The job to retrieve data for.

        Returns:
            JobData: JobData object with the job metadata.
        """
        try:
            self._validate_supabase_session()
            response = self._supabase.table(JOB_TABLE).select("*").eq("id", job.job_id).execute()
            return JobData(response.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to check the job status: {e}") from e
        
    def _get_job_executions(self, job: Job) -> list[JobExecution]:
        """
        Retrieves the results of all executions associated with a job.

        Args:
            job (Job): The job to retrieve executions for.

        Returns:
            list[JobExecution]: List of JobExecution objects for the job.
        """
        try:
            self._validate_supabase_session()
            response = self._supabase.table(JOB_EXECUTION_TABLE).select("*").eq("job_id", job.job_id).execute()
            return [JobExecution(JobExecutionData(row), job) for row in response.data]
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve job executions: {e}") from e
        
    def _get_execution(self, execution: JobExecution) -> JobExecutionData:
        """
        Retrieves the metadata of a specific job execution.

        Args:
            execution (JobExecution): The execution to retrieve data for.

        Returns:
            JobExecutionData: JobExecutionData object with the execution metadata.
        """
        try:
            self._validate_supabase_session()
            response = self._supabase.table(JOB_EXECUTION_TABLE).select("*").eq("id", execution.id).execute()
            return JobExecutionData(response.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to check the job execution status: {e}") from e

    def execute(self, circuit: QuantumCircuit, parameters: Optional[Union[dict[str, float], list[dict[str, float]]]] = None, shots: int = 1024, backend: str = default_backend) -> Job:
        """
        Queues circuit for execution with the specified backend and parameters.

        Args:
            circuit (QuantumCircuit): The circuit to be executed.
            parameters (Optional[Union[dict, list]]): Parameters for the circuit.
            shots (int): The number of shots for the circuit to execute.
            backend (str): The backend for the circuit to execute on.

        Returns:
            Job: Job object for the submitted job.

        Raises:
            TypeError: If the types of the arguments are incorrect.
        """

        if not isinstance(circuit, QuantumCircuit):
            raise TypeError("'circuit' must be of type QuantumCircuit")
        elif not isinstance(shots, int):
            raise TypeError("'shots' must be of type int")
        elif not isinstance(backend, str):
            raise TypeError("'backend' must be of type str")
        elif not isinstance(parameters, (dict, list, type(None))):
            raise TypeError("If provided, 'parameters' must be of type dict, or list[dict]")
        elif isinstance(parameters, list) and not all(
            isinstance(param, dict) and all(
                isinstance(k, str) and isinstance(v, numbers.Number) for k, v in param.items()
            ) for param in parameters
        ):
            raise TypeError("If provided as a list, 'parameters' must be a list of dicts with string keys and float values.")

        job_data, _ = self._execute_circuit(circuit, parameters, shots, backend)
        return Job(job_data, self)
        
    async def iterative_execute(
            self, 
            circuit: QuantumCircuit, 
            parameter_update_fn: Callable[[dict[str, int]], dict[str, float]], 
            initial_parameters: dict[str, float], 
            num_iterations: int = 10, 
            shots: int = 1024, 
            backend: str = default_backend, 
            timeout: float = 10000
    ) -> Job:
        """
        Iteratively executes a circuit, updating parameters after each iteration.

        Args:
            circuit (QuantumCircuit): The circuit to be executed.
            parameter_update_fn (Callable): Function to update parameters based on results.
            initial_parameters (dict): Initial parameters for the first iteration.
            num_iterations (int): Number of iterations.
            shots (int): Number of shots per execution.
            backend (str): Backend to execute on.
            timeout (float): Timeout for awaiting results.

        Returns:
            Job: Job object for the entire iterative execution.
        """
        job_data, execution_data_list = self._execute_circuit(circuit, initial_parameters, shots, backend, MultipleExecutionJob())
        job = Job(job_data, self)
        execution_id = execution_data_list[0]._id

        for i in range(num_iterations - 1):
            updated_job_data = await self._await_job_completion(job, timeout)
            if not updated_job_data:
                warnings.warn(f"Timed out on iteration {i + 1}", RuntimeWarning)
                return job
            
            job._update_from_data(updated_job_data)
            if job.get_status() == JobStatus.COMPLETED.value:
                executions = self._get_job_executions(job)
                execution_result = next((ex for ex in executions if ex.id == execution_id), None)

                if not execution_result or execution_result.get_status() != JobExecutionStatus.COMPLETED.value or not execution_result.get_counts():
                    warnings.warn(f"Unable to retrieve counts for iteration {i + 1}. Terminating.", RuntimeWarning)
                    return job
                
                try:
                    parameters = parameter_update_fn(execution_result.get_counts())
                    _, execution_data_list = self._execute_circuit(circuit, parameters, shots, backend, MultipleExecutionJob(override_job_id=job.job_id))
                    execution_id = execution_data_list[0]._id
                except Exception as e:
                    warnings.warn(f"Iteration {i + 2} failed with error: {str(e)}. Terminating.", RuntimeWarning)
                    return job
            else:
                warnings.warn(f"Job did not complete successfully in iteration {i + 1}. Terminating.", RuntimeWarning)
                return job
        
        return job

    def list_backends(self, provider: str = "all") -> Optional[Union[dict[str, list[str]], list[str]]]:
        """
        Fetches a list of all available quantum backends grouped by provider.

        Args:
            provider (str): Provider to retrieve backends for (default "all").

        Returns:
            Optional[Union[dict, list]]: A dictionary of providers to backends, a list of backends, or None.
        """
        self._validate_supabase_session()
        url = f"{self._base_url}/v1/backends"
        headers = {"Content-Type": "application/json", "Authorization": self._get_bearer_token()}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        backends = response.json()
        
        if provider == "all":
            return backends
        return backends.get(provider)

    def get_backend_stats(self, backend_name: str, provider: str) -> Optional[dict[str, Any]]:
        """
        Fetches statistics and configuration for a specific backend.

        Args:
            backend_name (str): The backend identifier.
            provider (str): The provider of the backend.
        
        Returns:
            Optional[dict]: Backend statistics and configuration, or None if not found.
        """
        if provider not in ["simulator", "ibm", "braket", "custom"]:
            warnings.warn(f"Provider {provider} not supported. Defaulting to simulator")
            provider = "simulator"
        
        self._validate_supabase_session()
        url = f"{self._base_url}/v1/backends/statistics"
        params = {"backend": backend_name, "provider": provider}
        headers = {"Content-Type": "application/json", "Authorization": self._get_bearer_token()}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return None
        return response.json()