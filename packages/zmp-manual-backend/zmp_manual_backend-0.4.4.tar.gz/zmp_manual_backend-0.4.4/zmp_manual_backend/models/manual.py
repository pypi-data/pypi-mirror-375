from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Union, Set, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


class SolutionType(str, Enum):
    ZCP = "zcp"
    APIM = "apim"
    AMDP = "amdp"


class ItemType(str, Enum):
    MANUAL = "manual"
    FOLDER = "folder"


class JobState(str, Enum):
    """States that match the flow diagram exactly, now with more granularity"""

    STARTED = "started"
    CHECKING_REPO = "checking_repo"
    CLONING = "cloning"
    MOVING_REPO = "moving_repo"
    CLEANING_UP = "cleaning_up"
    REMOVING_OLD_FILES = "removing_old_files"
    EXPORTING = "exporting"
    EXPORTING_CONTENT = "exporting_content"
    EXPORT_COMMIT = "export_commit"
    ENSURING_IMAGES = "ensuring_images"
    TRANSLATING = "translating"
    TRANSLATION_COMMIT = "translation_commit"
    PUSHING = "pushing"
    COMPLETED = "completed"
    FAILED = "failed"


class FailureReason(str, Enum):
    """Specific failure reasons matching diagram decision points"""

    REPO_ACCESS = "repository_access_failed"
    EXPORT_FAILED = "export_failed"
    TRANSLATION_FAILED = "translation_failed"
    GIT_OPERATION_FAILED = "git_operation_failed"
    UNKNOWN = "unknown_error"


class ManualBase(BaseModel):
    id: str
    title: str
    type: ItemType
    parent_id: Optional[str] = None
    notion_page_id: Optional[str] = None  # Add Notion page ID


class Manual(ManualBase):
    notion_url: HttpUrl
    path: str
    source_language: Optional[str] = "en"


class Folder(ManualBase):
    children: List[Union["Manual", "Folder"]] = []


# New model for Node objects from the exporter
class NodeModel(BaseModel):
    """Pydantic model that maps to Node objects from the exporter."""

    object_id: str
    title: str
    # These fields are optional to accommodate both manual and folder nodes
    parent_id: Optional[str] = None
    children: Optional[List["NodeModel"]] = None
    notion_url: Optional[str] = None
    path: Optional[str] = None
    last_edited_time: Optional[datetime] = None
    last_edited_by: Optional[str] = None
    last_editor_avatar_url: Optional[str] = None

    # Allow extra fields from Node objects
    class Config:
        extra = "allow"


# New response model for the API
class NodeList(BaseModel):
    """API response model that works with Node objects directly."""

    items: List[NodeModel]


class PublishRequest(BaseModel):
    """Request model for publishing a manual.
    When user selects a node from the tree view and clicks publish,
    the frontend will send:
    - notion_page_id: The Notion page ID of the selected node
    - selected_solution: The solution type (ZCP/APIM/AMDP)
    - target_languages: Optional list of target languages for translation
    - title: The title of the page to be published
    - is_directory: Whether the page is a directory
    - parent_id: Optional parent page ID in the hierarchy
    """

    notion_page_id: str  # Changed from root_page_id to notion_page_id to match frontend
    selected_solution: SolutionType
    target_languages: Optional[Set[str]] = None  # If None, use all configured languages
    title: Optional[str] = None  # Title of the page/directory
    is_directory: Optional[bool] = None  # Whether the page is a directory
    parent_id: Optional[str] = None  # Parent page ID in the hierarchy


class PublishStatus(BaseModel):
    """Model for tracking status of publishing process."""

    job_id: str
    status: JobState = JobState.STARTED
    message: Optional[str] = None
    total_progress: float = 0.0
    failure_reason: Optional[FailureReason] = None
    export_progress: float = 0.0
    translation_progress: float = 0.0
    export_files: int = 0
    notion_page_id: Optional[str] = None
    solution: Optional[str] = None
    initiated_by: Optional[str] = None  # User ID of who initiated this job
    title: Optional[str] = None  # Title of the page being published
    is_directory: Optional[bool] = None  # Whether the page is a directory
    parent_id: Optional[str] = None  # Parent page ID in the hierarchy

    # For backward compatibility
    @property
    def progress(self) -> float:
        """Alias for total_progress for backward compatibility."""
        return self.total_progress

    @progress.setter
    def progress(self, value: float):
        """Setter for progress that updates total_progress."""
        self.total_progress = value

    def update_status(
        self, status: JobState, message: str, total_progress: Optional[float] = None
    ):
        """Update status while preserving progress values."""
        self.status = status
        self.message = message
        if total_progress is not None:
            self.total_progress = total_progress

    def to_dict(self) -> Dict[str, Any]:
        """Convert status to dictionary."""
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "message": self.message,
            "total_progress": self.total_progress,
            "failure_reason": self.failure_reason.value
            if self.failure_reason
            else None,
            "export_progress": self.export_progress,
            "translation_progress": self.translation_progress,
            "export_files": self.export_files,
            "notion_page_id": self.notion_page_id,
            "solution": self.solution,
            "initiated_by": self.initiated_by,
            "title": self.title,
            "is_directory": self.is_directory,
            "parent_id": self.parent_id,
        }


class ManualList(BaseModel):
    items: List[Union[Manual, Folder]]


class NotificationStatus(str, Enum):
    """Status types of notifications"""

    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    PROCESSING = "processing"


class NotificationSourceType(str, Enum):
    """Source types of notifications"""

    JOB_RESULT = "job_result"  # For job completion/failure notifications
    DOCUMENT_UPDATE = "document_update"  # For document update/creation notifications
    SYSTEM = "system"  # For other system notifications


class Notification(BaseModel):
    """Model for notifications shown in the UI."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: NotificationStatus
    title: str
    message: str
    solution: Optional[SolutionType] = None
    user_id: Optional[str] = (
        None  # Add user_id to associate notifications with specific users
    )
    job_id: Optional[str] = (
        None  # Add job_id to associate notifications with specific jobs
    )
    created_at: datetime = Field(default_factory=datetime.now)
    is_read: bool = False
    document_title: Optional[str] = None  # Title of the Notion document being processed
    notification_type: NotificationSourceType = (
        NotificationSourceType.SYSTEM
    )  # Source type of notification
    node: Optional[Dict[str, Any]] = (
        None  # Node information for document_update notifications
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary."""
        return {
            "id": self.id,
            "status": self.status.value,
            "title": self.title,
            "message": self.message,
            "solution": self.solution.value if self.solution else None,
            "user_id": self.user_id,
            "job_id": self.job_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_read": self.is_read,
            "document_title": self.document_title,
            "notification_type": self.notification_type.value,
            "node": self.node,
        }


class SidebarMenuItem(BaseModel):
    """Model for a sidebar menu item."""

    name: str
    solution_type: SolutionType
    root_page_id: str


class SidebarMenu(BaseModel):
    """Model for the sidebar menu response."""

    solutions: List[SidebarMenuItem]


# This is needed for the forward reference in Folder
Manual.model_rebuild()
Folder.model_rebuild()
NodeModel.model_rebuild()  # For the self-reference in children
