from __future__ import annotations
from .job_execution import JobExecution
from warnings import warn
from typing import Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from .quave import Quave
    from .job_execution import JobExecution

class JobStatus(Enum):
    """Status of a job."""
    PENDING = "PENDING" # If any of the executions are still pending
    COMPLETED = "COMPLETED" # If all executions completed successfully
    FAILED = "FAILED" # If any execution failed and none are pending

class JobData:
    """Data wrapper for a job submitted to Quave."""
    _job_id: str
    _status: JobStatus
    _executed_at: Optional[datetime]
    _qasm: str
    _error: Optional[str]

    def __init__(
        self,
        data: Dict[str, Any]
    ):
        self._job_id = data.get("id")
        self._status = JobStatus(data.get("status"))
        executed_at = data.get("executed_at")
        self._executed_at = datetime.fromisoformat(executed_at) if executed_at else None
        self._qasm = data.get("qasm")
        self._error = data.get("error")
        self._validate_fields()

    def _validate_fields(self) -> None:
        """Validate that all required fields are present."""
        if not self._job_id or not self._status or not self._qasm:
            raise ValueError("JobData is missing required fields.")
        
    def _cached_in_final_state(self) -> bool:
        """
        Check if the job is in a final state.

        Returns:
            bool: True if the job is in a final state ("COMPLETED" or "FAILED"), False otherwise.
        """

        return self._status in [JobStatus.COMPLETED, JobStatus.FAILED]

class Job(JobData):
    """Job submitted to Quave."""
    _quave_client: Quave
    _in_final_state: bool

    def __init__(
        self,
        job_data: JobData,
        quave_client: Quave,
    ):
        self._job_id = job_data._job_id
        self._status = job_data._status
        self._executed_at = job_data._executed_at
        self._qasm = job_data._qasm
        self._error = job_data._error
        self._quave_client = quave_client
        self._in_final_state = self._cached_in_final_state()
        self._validate_fields()

    def _update_from_data(self, job_data: JobData) -> None:
        """Update the job data from a dictionary and refresh final state cache."""
        self._job_id = job_data._job_id
        self._status = job_data._status
        self._executed_at = job_data._executed_at
        self._qasm = job_data._qasm
        self._error = job_data._error
        self._in_final_state = self._cached_in_final_state()
        self._validate_fields()

    def _validate_fields(self) -> None:
        """Validate that all required fields are present."""

        super()._validate_fields()
        if not self._quave_client:
            raise ValueError("Job must have a valid Quave client.")
        
        if self._in_final_state and (not self._executed_at):
            warn("Job in final state but missing time of execution.")

    def _refetch(self) -> None:
        """Refetch job data and update attributes"""
        data = self._quave_client._get_job(self)
        self._update_from_data(data)
    
    @property
    def job_id(self) -> str:
        return self._job_id
    
    @property
    def qasm(self) -> str:
        return self._qasm
    
    def get_status(self) -> str:
        """
        Fetch the current status of the job.

        Returns:
            str: Current status of the job ("PENDING", "COMPLETED", or "FAILED")

        Raises:
            RuntimeError: If there was an error retrieving the job status.
        """

        if self._in_final_state:
            return self._status.value
        
        self._refetch()
        return self._status.value
    
    def get_executed_at(self) -> Optional[datetime]:
        """
        Fetch the time of execution for the job.

        Returns:
            Optional[datetime]: Execution time of the job or None if not executed yet.

        Raises:
            RuntimeError: If there was an error retrieving the execution time.
        """

        if self._in_final_state:
            return self._executed_at
        
        self._refetch()
        return self._executed_at
    
    def get_error(self) -> Optional[str]:
        """
        Fetch the error message of the job if it failed.

        Returns:
            Optional[str]: Error message if the job failed, otherwise None.

        Raises:
            RuntimeError: If there was an error retrieving the error message.
        """

        if self._in_final_state:
            return self._error
        
        self._refetch()
        return self._error
    
    def get_executions(self) -> list[JobExecution]:
        """
        Fetch all executions associated with this job.
        
        Returns:
            list[JobExecution]: List of JobExecution objects associated with this job.

        Raises:
            RuntimeError: If there was an error retrieving the executions.
        """

        # Retrieve JobExecutionData
        execution_data_list = self._quave_client._get_job_executions(self)

        from .job_execution import JobExecution
        # Parse into returned JobExecution objects
        executions = [JobExecution(execution, self) for execution in execution_data_list]
        return executions
    
    async def await_completion(self, timeout: float = 1000.0) -> bool:
        """
        Waits for a job to be complete and then updates the Job attributes asyncronously

        Args:
            timout (float): Amount of seconds to wait before exiting without a result - default = 1,0000

        Returns:
            bool: Whether the job finished within the timeout period

        Raises:
            ValueError: If the updated job data is incomplete or missing required fields
            RuntimeWarning: If the job timed out
        """

        # Await job completion for timeout period
        job_data = await self._quave_client._await_job_completion(self, timeout)

        # Update job data on successful completion
        if job_data:
            self._update_from_data(job_data)
            return True
    
        # Indicate timeout
        else:
            return False
