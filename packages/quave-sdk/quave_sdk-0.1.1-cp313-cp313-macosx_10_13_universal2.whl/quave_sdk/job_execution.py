from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from enum import Enum
from datetime import datetime

if TYPE_CHECKING:
    from .quave import Quave
    from .job import Job

class JobExecutionStatus(Enum):
    """Status of a job execution."""
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PENDING = "PENDING"

class JobExecutionData:
    """Data structure representing a single execution within a Job."""
    _id: str
    _job_id: str
    _counts: Optional[dict[str, int]]
    _parameters: Optional[dict[str, float]]
    _status: JobExecutionStatus
    _queued_at: datetime
    _executed_at: Optional[datetime]
    _provider: str
    _backend_name: str
    _backend_version: Optional[str]
    _hardware_id: Optional[str]
    _shots: int
    _error: Optional[str]

    def __init__ (self, data: dict[str, Any]):
        self._id = data.get('id')
        self._job_id = data.get('job_id')
        self._counts = data.get('counts')
        self._parameters = data.get('parameters')
        self._status = JobExecutionStatus(data.get('status'))
        queued_at = data.get("queued_at")
        self._queued_at = datetime.fromisoformat(queued_at) if queued_at else None
        executed_at = data.get("executed_at")
        self._executed_at = datetime.fromisoformat(executed_at) if executed_at else None
        self._provider = data.get('provider')
        self._backend_name = data.get('backend_name')
        self._backend_version = data.get('backend_version')
        self._hardware_id = data.get('hardware_id')
        self._shots = data.get('shots')
        self._error = data.get('error')
        self._validate_fields()

    def _validate_fields(self) -> None:
        """Validate that all required fields are present."""
        if not self._id or not self._job_id or not self._status or not self._provider or not self._backend_name or not self._shots:
            raise ValueError("JobExecutionData is missing required fields.")
        if self._status == JobExecutionStatus.COMPLETED and (not self._counts or not self._executed_at or not self._backend_version or not self._hardware_id):
            raise ValueError("Completed JobExecutionData is missing required fields.")
        
    def _cached_in_final_state(self) -> bool:
        """
        Check if the execution is in a final state.

        Returns:
            bool: True if the execution is in a final state, False otherwise.
        """
        return self._status in [JobExecutionStatus.COMPLETED, JobExecutionStatus.FAILED]

class JobExecution(JobExecutionData):
    """A single execution within a Job."""
    _job: Job
    _quave_client: Quave
    _in_final_state: bool

    def __init__ (self, job_execution_data: JobExecutionData, job: Job):
        self.__dict__.update(job_execution_data.__dict__)
        self._job = job
        self._quave_client = job._quave_client
        self._in_final_state = self._cached_in_final_state()
        self._validate_fields()

    def _validate_fields(self) -> None:
        """Validate that all required fields are present."""
        super()._validate_fields()
        if not self._quave_client:
            raise ValueError("JobExecution must have a valid Quave client.")
        if self._job_id != self._job.job_id:
            raise ValueError("The referenced Job object does not align with the initialised job_id")

    def _update_from_data(self, job_execution_data: JobExecutionData) -> None:
        """Update the execution data from a JobExecutionData object and refresh final state cache."""
        self.__dict__.update(job_execution_data.__dict__)
        self._in_final_state = self._cached_in_final_state()
        self._validate_fields()

    def _refetch(self) -> None:
        """Refetch execution data and update attributes"""
        data = self._quave_client._get_execution(self)
        self._update_from_data(data)

    @property
    def id(self) -> str:
        """Get the execution ID."""
        return self._id
    
    @property
    def parameters(self) -> Optional[dict[str, Any]]:
        """Get the parameters used for the execution."""
        return self._parameters
    
    @property
    def queued_at(self) -> datetime:
        """Get the time the execution was queued."""
        return self._queued_at
    
    @property
    def backend_name(self) -> str:
        """Get the name of the backend used for the execution."""
        return self._backend_name
    
    @property
    def provider(self) -> str:
        """Get the provider of the backend used for the execution."""
        return self._provider
    
    @property
    def shots(self) -> int:
        """Get the number of shots used in the execution."""
        return self._shots
    
    def get_counts(self) -> Optional[dict[str, int]]:
        """Get the measurement counts from the execution."""
        if self._in_final_state:
            return self._counts
        self._refetch()
        return self._counts
    
    def get_status(self) -> str:
        """Get the current status of the execution."""
        if self._in_final_state:
            return self._status.value
        self._refetch()
        return self._status.value
    
    def get_executed_at(self) -> Optional[datetime]:
        """Get the time the execution was executed."""
        if self._in_final_state:
            return self._executed_at
        self._refetch()
        return self._executed_at
    
    def get_backend_version(self) -> Optional[str]:
        """Get the version of the backend used for the execution."""
        if self._in_final_state:
            return self._backend_version
        self._refetch()
        return self._backend_version
    
    def get_hardware_id(self) -> Optional[str]:
        """Get the hardware ID used for the execution."""
        if self._in_final_state:
            return self._hardware_id
        self._refetch()
        return self._hardware_id
    
    def get_error(self) -> Optional[str]:
        """Get the error message if the execution failed."""
        if self._in_final_state:
            return self._error
        self._refetch()
        return self._error
    
    def get_job(self) -> Job:
        """Get the parent Job object."""
        if self._job._cached_in_final_state():
            return self._job
        self._job._refetch()
        return self._job
    
    async def await_completion(self, timeout: float = 1000.0) -> bool:
        """
        Waits for a job execution to be complete and then updates attributes asynchronously.

        Args:
            timeout (float): Amount of seconds to wait before exiting.

        Returns:
            bool: Whether the job execution finished within the timeout period.
        """
        execution_data = await self._quave_client._await_execution_completion(self, timeout)
        if execution_data:
            self._update_from_data(execution_data)
            return True
        return False