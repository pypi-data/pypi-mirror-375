from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Path as FastAPIPath,
    BackgroundTasks,
    Depends,
    Request,
    Header,
)
from sse_starlette.sse import EventSourceResponse
from zmp_manual_backend.core.manual_service import ManualService
from zmp_manual_backend.models.manual import (
    PublishRequest,
    PublishStatus,
    JobState,
    SolutionType,
    SidebarMenu,
    SidebarMenuItem,
    FailureReason,
    NotificationStatus,
    NotificationSourceType,
)
from zmp_manual_backend.models.auth import TokenData
from zmp_manual_backend.api.oauth2_keycloak import get_current_user
import asyncio
import os
from dotenv import load_dotenv
from typing import List, Optional, Dict, Tuple
import logging
from pathlib import Path
import uuid
import time
from datetime import datetime
import json
import hmac
import hashlib
from pydantic import BaseModel, Field
from collections import OrderedDict
import shutil

# Load environment variables from the project root directory
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"

# Parse VSCODE_ENV_REPLACE for environment variables
vscode_env = os.environ.get("VSCODE_ENV_REPLACE", "")
if vscode_env:
    # Split by : and parse each key=value pair
    env_pairs = vscode_env.split(":")
    for pair in env_pairs:
        if "=" in pair:
            key, value = pair.split("=", 1)
            # Only set if the value is not empty
            if value:
                os.environ[key] = value.replace("\\x3a", ":")  # Fix escaped colons

# Load .env file as fallback
load_dotenv(dotenv_path=env_path)

router = APIRouter()
logger = logging.getLogger("appLogger")

# Cache for processed webhook events with timestamp
_processed_events: Dict[str, float] = OrderedDict()
# Cache for processed page updates with timestamp
_processed_pages: Dict[Tuple[str, str], float] = (
    OrderedDict()
)  # (page_id, solution) -> timestamp
_MAX_CACHE_SIZE = 1000
_EVENT_TTL = 3600  # 1 hour TTL for processed events
_PAGE_UPDATE_COOLDOWN = 60  # 60 seconds cooldown between updates for the same page


def _cleanup_old_events():
    """Remove events older than TTL from the cache"""
    current_time = time.time()
    # Clean up events
    for event_id, timestamp in list(_processed_events.items()):
        if current_time - timestamp > _EVENT_TTL:
            _processed_events.pop(event_id, None)

    # Clean up page updates
    for page_key, timestamp in list(_processed_pages.items()):
        if current_time - timestamp > _EVENT_TTL:
            _processed_pages.pop(page_key, None)

    # If still too large, remove oldest events
    while len(_processed_events) > _MAX_CACHE_SIZE:
        _processed_events.popitem(last=False)
    while len(_processed_pages) > _MAX_CACHE_SIZE:
        _processed_pages.popitem(last=False)


# Add these models at the top level, after imports
class NotionVerificationRequest(BaseModel):
    """Model for Notion's URL verification request"""

    type: str = Field(
        ..., description="Must be 'url_verification' for verification requests"
    )
    challenge: str = Field(..., description="Challenge token that must be echoed back")


class NotionWebhookRequest(BaseModel):
    type: str
    page: dict


class NotionAuthor(BaseModel):
    id: str = Field(..., description="The unique identifier of the author")
    type: str = Field("person", description="The type of the author, usually 'person'")


class NotionEntity(BaseModel):
    id: str = Field(..., description="The unique identifier of the entity")
    type: str = Field(
        ..., description="The type of the entity (e.g., 'page', 'database')"
    )


class NotionParent(BaseModel):
    id: str = Field(..., description="The unique identifier of the parent")
    type: str = Field(
        ..., description="The type of the parent (e.g., 'page', 'database')"
    )


class NotionWebhookData(BaseModel):
    page_id: Optional[str] = Field(None, description="The ID of the affected page")
    parent: Optional[NotionParent] = Field(None, description="Parent information")
    challenge: Optional[str] = Field(
        None, description="Challenge token for verification requests"
    )


class NotionWebhookEvent(BaseModel):
    """Model for Notion webhook events"""

    id: str = Field(..., description="The unique ID of the webhook event")
    timestamp: str = Field(
        ..., description="ISO 8601 formatted time at which the event occurred"
    )
    workspace_id: str = Field(
        ..., description="The workspace ID where the event originated"
    )
    workspace_name: Optional[str] = Field(None, description="The name of the workspace")
    type: str = Field(
        ...,
        description="The type of the event (e.g., 'page.updated', 'url_verification')",
    )
    authors: List[NotionAuthor] = Field(
        ..., description="List of authors involved in the event"
    )
    entity: NotionEntity = Field(..., description="The entity that was affected")
    data: NotionWebhookData = Field(
        ..., description="Additional data specific to the event"
    )


# Add this model for the actual verification token format
class NotionVerificationTokenRequest(BaseModel):
    """Model for Notion's verification token request"""

    verification_token: str


# Create a custom JSON encoder that can handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling datetime objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def initialize_manual_service() -> ManualService:
    """Initialize and return a ManualService instance."""
    try:
        notion_token = os.environ.get("NOTION_TOKEN")
        if not notion_token:
            logger.error("NOTION_TOKEN not found in environment variables")
            logger.error(f"Looking for .env file at: {env_path}")
            logger.error(f".env file exists: {env_path.exists()}")
            raise ValueError("NOTION_TOKEN environment variable is not set")

        logger.info(f"Initializing manual service with token: {notion_token[:5]}...")

        # Log the available root page IDs
        for solution in ["ZCP", "APIM", "AMDP"]:
            env_var = f"{solution}_ROOT_PAGE_ID"
            if os.environ.get(env_var):
                logger.info(f"Found {env_var} in environment variables")

        return ManualService(
            notion_token=notion_token,
            root_page_id=os.environ.get(
                "ZCP_ROOT_PAGE_ID"
            ),  # For backward compatibility
            repo_path=os.environ.get("REPO_BASE_PATH", "./repo"),
            source_dir=os.environ.get("SOURCE_DIR", "docs"),
            target_dir=os.environ.get("TARGET_DIR", "i18n"),
            github_repo_url=os.environ.get("GITHUB_REPO_URL"),
            github_branch=os.environ.get("GITHUB_BRANCH", "develop"),
            target_languages=set(
                lang.strip()
                for lang in os.environ.get("TARGET_LANGUAGES", "ko,ja,zh").split(",")
            ),
            cache_path=os.environ.get("CACHE_BASE_PATH", "./cache"),
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            openai_model=os.environ.get("OPENAI_MODEL"),
            max_chunk_size=os.environ.get("MAX_CHUNK_SIZE"),
            max_concurrent_requests=os.environ.get("MAX_CONCURRENT_REQUESTS"),
        )
    except Exception as e:
        logger.error(f"Failed to initialize manual service: {str(e)}")
        raise


# Initialize service instance
manual_service = initialize_manual_service()


def get_manual_service() -> ManualService:
    """Dependency function to get the ManualService instance."""
    return manual_service


@router.get("/manuals")
async def get_manuals(
    selected_solution: SolutionType = Query(
        default=SolutionType.ZCP,
        description="The solution type to retrieve manuals for (zcp, apim, amdp)",
    ),
):
    """Get hierarchical list of manuals and folders for the specified solution"""
    try:
        items = await manual_service.get_manuals(selected_solution=selected_solution)

        # Get all nodes in a flat structure to debug the issue
        all_nodes = get_all_nodes_recursive(items)
        logger.info(f"Found {len(all_nodes)} total nodes for {selected_solution.value}")

        # Convert Node objects to dictionaries
        items_dicts = []
        for item in all_nodes:
            item_dict = {
                "object_id": item.object_id,
                "title": item.name,
                "is_directory": item.is_directory,
                "parent_id": item.parent.object_id if item.parent else None,
                "notion_url": item.notion_url,
                "index": item.index,
                "last_edited_time": item.last_edited_time,
                "last_edited_by": item.last_edited_by,
                "last_editor_avatar_url": item.last_editor_avatar_url,
            }
            items_dicts.append(item_dict)

        return {"items": items_dicts}
    except Exception as e:
        logger.error(f"Error getting manuals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def get_all_nodes_recursive(nodes, collected_nodes=None):
    """Get all nodes in the tree, including children.

    Args:
        nodes: A list of root nodes
        collected_nodes: Internal parameter for recursion

    Returns:
        List of all nodes in the tree
    """
    if collected_nodes is None:
        collected_nodes = []

    for node in nodes:
        collected_nodes.append(node)

        # Recursively add all children
        if hasattr(node, "children") and node.children:
            get_all_nodes_recursive(node.children, collected_nodes)

    return collected_nodes


async def robust_rmtree(path, retries=3, delay=300):
    """Async version: Robustly remove a directory, handling NFS .nfs* files and retrying on failure.
    The delay between retries increases by 5 minutes (300 seconds) after each failure."""
    import os

    for i in range(retries):
        try:
            await asyncio.to_thread(shutil.rmtree, path)
            return True
        except Exception as e:
            logger.warning(f"Delete failed: {e}")
            # Try to remove .nfs* files if present
            for root, dirs, files in await asyncio.to_thread(
                lambda: list(os.walk(path))
            ):
                for f in files:
                    if f.startswith(".nfs"):
                        try:
                            await asyncio.to_thread(os.remove, os.path.join(root, f))
                        except Exception as e2:
                            logger.warning(f"Failed to remove {f}: {e2}")
            wait_time = delay + i * 300  # Increase by 5 minutes (300 seconds) per retry
            logger.warning(
                f"Waiting {wait_time} seconds before next retry to delete {path}"
            )
            await asyncio.sleep(wait_time)
    logger.warning(f"Failed to delete {path} after {retries} retries")
    return False


@router.post(
    "/publish", openapi_extra={"security": [{"OAuth2AuthorizationCodeBearer": []}]}
)
async def publish_manual(
    request: PublishRequest,
    background_tasks: BackgroundTasks,
    manual_service: ManualService = Depends(get_manual_service),
    current_user: TokenData = Depends(get_current_user),
) -> dict:
    """Publish a manual by exporting it from Notion and translating it."""
    try:
        if not request.notion_page_id:
            raise HTTPException(status_code=400, detail="notion_page_id is required")

        user_id = current_user.username

        # Generate job ID and create initial status with complete information
        job_id = str(uuid.uuid4())
        solution_value = (
            request.selected_solution.value
            if isinstance(request.selected_solution, SolutionType)
            else request.selected_solution
        )

        manual_service.active_jobs[job_id] = PublishStatus(
            job_id=job_id,
            status=JobState.STARTED,
            message="Starting publication process",
            progress=0.0,
            notion_page_id=request.notion_page_id,  # Set notion_page_id immediately
            solution=solution_value,  # Set solution immediately
            initiated_by=current_user.username,  # Track which user initiated this job
            title=request.title,  # Add title information
            is_directory=request.is_directory,  # Add is_directory information
            parent_id=request.parent_id,  # Add parent_id information
        )

        # Define an error handler for the background task
        async def publish_and_remove_the_job_directory():
            try:
                await manual_service.publish_manual(
                    request.notion_page_id,
                    request.selected_solution,
                    request.target_languages,
                    user_id,
                    job_id=job_id,  # Pass the job_id explicitly
                    title=request.title,  # Pass title
                    is_directory=request.is_directory,  # Pass is_directory
                    parent_id=request.parent_id,  # Pass parent_id
                )
            except Exception as e:
                logger.error(f"Background task error in publish: {str(e)}")
                # Make sure job is marked as failed if there's an unhandled exception
                if job_id in manual_service.active_jobs:
                    manual_service.active_jobs[job_id].status = JobState.FAILED
                    manual_service.active_jobs[
                        job_id
                    ].message = f"Publication failed: {str(e)}"
                    manual_service.active_jobs[
                        job_id
                    ].failure_reason = FailureReason.UNKNOWN
            finally:
                # Only delete the current job directory after completion
                job_dir = os.path.join(manual_service.original_repo_path, job_id)
                try:
                    if os.path.exists(job_dir):
                        await robust_rmtree(job_dir)
                        logger.info(f"Deleted job directory: {job_dir}")
                except Exception as e:
                    logger.warning(
                        f"Failed to delete job directory {job_dir}: {str(e)}"
                    )

        # Add the error-handled publication process to background tasks
        background_tasks.add_task(publish_and_remove_the_job_directory)

        logger.info(
            f"Created job {job_id} for publishing manual (running in background)"
        )

        # Return the job ID to the client immediately
        return {"job_id": job_id}
    except ValueError as e:
        logger.error(f"Validation error in publish request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting publication: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}", response_model=Optional[PublishStatus])
async def get_job_status(
    job_id: str = FastAPIPath(..., description="The ID of the job to check"),
    manual_service: ManualService = Depends(get_manual_service),
):
    """Get current status of a publication job"""
    try:
        logger.info(f"Fetching status for job: {job_id}")
        status = await manual_service.get_job_status(job_id)
        if not status:
            logger.warning(f"Job not found: {job_id}")
            raise HTTPException(status_code=404, detail="Job not found")
        logger.info(f"Job {job_id} status: {status.status}")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watch/{job_id}")
async def watch_publication(
    job_id: str = FastAPIPath(..., description="The ID of the job to watch"),
    current_user: TokenData = Depends(get_current_user),
    manual_service: ManualService = Depends(get_manual_service),
):
    """Watch publication progress using Server-Sent Events"""
    try:
        # Check if job exists first
        status = await manual_service.get_job_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")

        # Check if the current user is authorized to watch this job
        if (
            hasattr(status, "initiated_by")
            and status.initiated_by
            and status.initiated_by != current_user.username
        ):
            if current_user.username not in ["cloudzcp-admin", "admin"]:
                raise HTTPException(
                    status_code=403, detail="Not authorized to watch this job"
                )

        logger.info(
            f"Starting SSE stream for job {job_id} by user {current_user.username}"
        )

        async def event_generator():
            retry_count = 0
            max_retries = 5  # Increased max retries
            ping_interval = 10  # Send ping every 10 seconds
            last_ping_time = time.time()
            last_status_json = None
            completion_time = None
            error_sent = False  # Track if we've sent an error event

            # Initial status update to client
            initial_status = await manual_service.get_job_status(job_id)
            if initial_status:
                # Set full tree path as title if possible
                if initial_status.notion_page_id and initial_status.solution:
                    full_title = manual_service.get_full_title_path(
                        initial_status.notion_page_id,
                        SolutionType(initial_status.solution),
                    )
                    if full_title:
                        initial_status.title = full_title
                # Convert PublishStatus to dictionary format for consistent response format
                status_dict = initial_status.to_dict()
                status_json = json.dumps(
                    status_dict, separators=(",", ":"), cls=DateTimeEncoder
                )
                yield {"data": status_json}
                last_status_json = status_json
                logger.info(
                    f"Sent initial job status: {initial_status.status} for job {job_id}"
                )

                # If already in completed state, set completion time to start shutdown sequence
                if initial_status.status in [
                    JobState.COMPLETED,
                    JobState.FAILED,
                ]:
                    completion_time = time.time()
                    logger.info(
                        f"Job {job_id} already in completed state: {initial_status.status}"
                    )

            while True:
                try:
                    current_time = time.time()

                    # Check if we need to send a ping
                    if current_time - last_ping_time >= ping_interval:
                        ping_data = f"ping - {datetime.now().isoformat()}"
                        yield {"event": "ping", "data": ping_data}
                        logger.debug(f"Sent ping: {ping_data} for job {job_id}")
                        last_ping_time = current_time

                    # Get latest job status
                    status = await manual_service.get_job_status(job_id)
                    if not status:
                        if retry_count >= max_retries:
                            logger.warning(
                                f"Job {job_id} not found after {max_retries} retries"
                            )
                            if not error_sent:
                                yield {"event": "info", "data": "Job not found"}
                                error_sent = True
                            break
                        retry_count += 1
                        await asyncio.sleep(1)
                        continue

                    # Reset retry count if we successfully got a status
                    retry_count = 0

                    # Set full tree path as title if possible
                    if status and status.notion_page_id and status.solution:
                        full_title = manual_service.get_full_title_path(
                            status.notion_page_id, SolutionType(status.solution)
                        )
                        if full_title:
                            status.title = full_title

                    # Convert PublishStatus to dictionary format for consistent response format
                    status_dict = status.to_dict()
                    status_json = json.dumps(
                        status_dict, separators=(",", ":"), cls=DateTimeEncoder
                    )

                    # Only send update if status changed
                    if status_json != last_status_json:
                        yield {"data": status_json}
                        last_status_json = status_json
                        logger.info(
                            f"Sent job status update: {status.status} for job {job_id}"
                        )

                    # Check if job is completed
                    if status.status in [
                        JobState.COMPLETED,
                        JobState.FAILED,
                    ]:
                        if completion_time is None:
                            # Record when the job completed
                            completion_time = time.time()
                            logger.info(
                                f"Job {job_id} completed with status {status.status}, will keep connection alive for a while"
                            )

                            # For FAILED, send an info message rather than error to avoid connection issues
                            if status.status == JobState.FAILED:
                                yield {
                                    "event": "info",
                                    "data": f"Job failed: {status.message or 'Unknown error'}",
                                }

                            # Always send the full status json as a data event
                            yield {"data": status_json}

                        # Keep the connection alive for a short period after completion
                        # to ensure the client receives the final status
                        elif (
                            time.time() - completion_time > 15
                        ):  # Increased grace period to 15 seconds
                            logger.info(
                                f"Closing SSE stream for job {job_id} after completion grace period"
                            )
                            # Send one final ping before closing
                            yield {
                                "event": "ping",
                                "data": f"final - {datetime.now().isoformat()}",
                            }
                            break

                    # Sleep shorter intervals to ensure more responsive updates
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error in event stream for job {job_id}: {str(e)}")
                    retry_count += 1

                    if retry_count >= max_retries:
                        if not error_sent:
                            logger.warning(
                                f"Too many errors in stream for job {job_id}, sending error and closing"
                            )
                            yield {"event": "info", "data": f"Stream error: {str(e)}"}
                            error_sent = True
                            # Don't break immediately, give the client a chance to receive the error
                            completion_time = completion_time or time.time()
                        elif time.time() - (completion_time or time.time()) > 5:
                            break

                    await asyncio.sleep(1)

        return EventSourceResponse(
            event_generator(),
            ping=None,  # Disable automatic pings, we'll handle them manually
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting up event stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs", response_model=List[PublishStatus])
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100, description="Number of jobs to return"),
    manual_service: ManualService = Depends(get_manual_service),
):
    """List recent publication jobs with optional status filter"""
    try:
        # Get all jobs from the manual service
        jobs = list(manual_service.active_jobs.values())
        logger.info(f"Found {len(jobs)} active jobs")

        if status:
            jobs = [job for job in jobs if job.status == status]

        # Sort by most recent first (assuming job_id contains timestamp)
        jobs.sort(key=lambda x: x.job_id, reverse=True)

        return jobs[:limit]
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/stream")
async def stream_notifications(
    include_read: bool = Query(
        False, description="Whether to include read notifications"
    ),
    manual_service: ManualService = Depends(get_manual_service),
):
    """Stream all notifications in real-time using Server-Sent Events (SSE)."""
    try:
        logger.info("Starting notification stream for all jobs")

        async def event_generator():
            notification_queue = asyncio.Queue()
            ping_interval = 10  # Send ping every 10 seconds
            last_ping_time = time.time()

            # Register client without specific user_id for global notifications
            queue_id = await manual_service.register_notification_client(
                queue=notification_queue, user_id=None
            )
            logger.info(
                f"Registered notification client {queue_id} for global notifications"
            )

            try:
                # First send existing notifications
                notifications = await manual_service.get_notifications(
                    include_read=include_read,
                    limit=10,  # Limit to recent notifications only
                )

                # Send the latest notification if any exist
                if notifications:
                    latest = notifications[0]  # Already sorted newest first
                    notification_data = latest.to_dict()
                    if latest.job_id and latest.job_id in manual_service.active_jobs:
                        job_status = manual_service.active_jobs[latest.job_id]
                        if job_status.title:
                            notification_data["document_title"] = job_status.title

                    notification_json = json.dumps(
                        notification_data, separators=(",", ":"), cls=DateTimeEncoder
                    )
                    yield {"data": notification_json}
                    logger.info(
                        "Sent initial notification to global notification stream"
                    )

                # Then listen for new notifications
                while True:
                    current_time = time.time()

                    # Send periodic ping with retry directive
                    if current_time - last_ping_time >= ping_interval:
                        ping_data = f"ping - {datetime.now().isoformat()}"
                        yield {
                            "event": "ping",
                            "data": ping_data,
                            "retry": 5000,  # Reconnect after 5 seconds if connection lost (as integer)
                        }
                        logger.debug(f"Sent ping to notification stream: {ping_data}")
                        last_ping_time = current_time

                    # Use a timeout to allow for periodic pings even when there are no notifications
                    try:
                        notification = await asyncio.wait_for(
                            notification_queue.get(), timeout=0.5
                        )
                    except asyncio.TimeoutError:
                        # No notification received within timeout, continue loop
                        continue

                    if notification is None:  # None is our signal to stop
                        logger.info("Notification stream closing")
                        break

                    # Skip read notifications unless explicitly included
                    if not include_read and notification.is_read:
                        notification_queue.task_done()
                        continue

                    # Send the notification with enhanced data
                    try:
                        # Convert to dict first to enhance with additional data
                        notification_data = notification.to_dict()

                        # Add document title to notification if job_id exists
                        if (
                            notification.job_id
                            and notification.job_id in manual_service.active_jobs
                            and not notification.document_title
                        ):
                            job_status = manual_service.active_jobs[notification.job_id]
                            if job_status.title:
                                notification_data["document_title"] = job_status.title

                        notification_json = json.dumps(
                            notification_data,
                            separators=(",", ":"),
                            cls=DateTimeEncoder,
                        )
                        yield {"data": notification_json}
                        logger.debug(
                            f"Sent notification {notification.id} to notification stream"
                        )
                    except Exception as e:
                        logger.error(f"Error serializing notification: {str(e)}")

                    # Mark the item as processed
                    notification_queue.task_done()

            finally:
                # Always unregister client to avoid memory leaks
                await manual_service.unregister_notification_client(queue_id)
                logger.info(f"Unregistered notification client {queue_id}")

        return EventSourceResponse(
            event_generator(),
            ping=None,  # Disable automatic pings, we're handling them manually
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable buffering in nginx
                "Access-Control-Allow-Origin": "*",  # Allow CORS
                "Content-Type": "text/event-stream;charset=utf-8",
            },
        )
    except Exception as e:
        logger.error(f"Error in notification stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str = FastAPIPath(
        ..., description="The ID of the notification to mark as read"
    ),
    manual_service: ManualService = Depends(get_manual_service),
):
    """Mark a notification as read."""
    try:
        success = await manual_service.mark_notification_read(notification_id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/clear")
async def clear_notifications(
    manual_service: ManualService = Depends(get_manual_service),
):
    """Clear all notifications."""
    try:
        await manual_service.clear_notifications()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error clearing notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sidebar", response_model=SidebarMenu)
async def get_sidebar_menu(
    manual_service: ManualService = Depends(get_manual_service),
):
    """Get information about all available solutions for the sidebar menu."""
    try:
        solutions = []
        for solution_type in SolutionType:
            root_page_id = manual_service.root_page_ids.get(solution_type)
            if root_page_id:
                solutions.append(
                    SidebarMenuItem(
                        name=solution_type.value.upper(),
                        solution_type=solution_type,
                        root_page_id=root_page_id,
                    )
                )

        return SidebarMenu(solutions=solutions)
    except Exception as e:
        logger.error(f"Error getting sidebar menu: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_notion_webhook(
    request: Request,
    solution_type: SolutionType,
    manual_service: ManualService,
    background_tasks: BackgroundTasks,
    x_notion_signature: Optional[str] = None,
) -> dict:
    """Common webhook processing logic for all solution-specific endpoints."""
    try:
        body = await request.body()
        body_text = body.decode()
        body_json = json.loads(body_text)

        logger.info(
            f"Received webhook request for {solution_type.value} with body: {body_text}"
        )

        # Handle verification request (special case)
        if "verification_token" in body_json:
            logger.info(
                f"Received Notion webhook verification request for {solution_type.value}"
            )
            verification_request = NotionVerificationTokenRequest(**body_json)
            return {"verification_token": verification_request.verification_token}

        # Check for duplicate events by event ID
        event_id = body_json.get("id")
        if event_id and event_id in _processed_events:
            logger.info(
                f"Skipping duplicate event {event_id} for {solution_type.value}"
            )
            return {
                "status": "accepted",
                "message": "Event already processed",
                "event_id": event_id,
                "timestamp": datetime.now().isoformat(),
            }

        # Parse the webhook event
        webhook_event = NotionWebhookEvent(**body_json)

        # Extract page ID
        notion_page_id = None
        if webhook_event.type.startswith("page."):
            notion_page_id = webhook_event.entity.id
        elif webhook_event.data.page_id:
            notion_page_id = webhook_event.data.page_id

        if notion_page_id:
            # Check for recent updates to this page
            page_key = (notion_page_id, solution_type.value)
            current_time = time.time()
            last_update = _processed_pages.get(page_key)

            if last_update and (current_time - last_update) < _PAGE_UPDATE_COOLDOWN:
                logger.info(
                    f"Skipping update for page {notion_page_id} - too soon after last update"
                )
                return {
                    "status": "accepted",
                    "message": f"Update skipped - page was recently updated ({int(current_time - last_update)} seconds ago)",
                    "page_id": notion_page_id,
                    "timestamp": datetime.now().isoformat(),
                }

            # Record this update
            _processed_pages[page_key] = current_time

        # Record the event ID
        if event_id:
            _processed_events[event_id] = time.time()

        # Cleanup old entries
        _cleanup_old_events()

        # For actual webhook events, validate the signature if present
        if x_notion_signature:
            # Get the solution-specific webhook secret
            webhook_secret_key = f"NOTION_WEBHOOK_{solution_type.value.upper()}_SECRET"
            verification_token = os.environ.get(webhook_secret_key)

            if verification_token:
                # Calculate HMAC using the raw body
                hmac_obj = hmac.new(
                    verification_token.encode(),
                    body,  # Use raw body bytes, not decoded text
                    hashlib.sha256,
                )
                calculated_signature = f"sha256={hmac_obj.hexdigest()}"

                logger.info(f"Using webhook secret for {solution_type.value}")
                logger.info(f"Raw body used for signature: {body_text}")
                logger.info(f"Calculated signature: {calculated_signature}")
                logger.info(f"Received signature: {x_notion_signature}")

                # Use constant-time comparison to prevent timing attacks
                if not hmac.compare_digest(
                    calculated_signature.encode(), x_notion_signature.encode()
                ):
                    logger.warning(
                        f"Invalid webhook signature for {solution_type.value}"
                    )
                    logger.warning(f"Expected: {calculated_signature}")
                    logger.warning(f"Received: {x_notion_signature}")
                    raise HTTPException(status_code=401, detail="Invalid signature")
            else:
                logger.warning(
                    f"No webhook secret found for {solution_type.value} (missing {webhook_secret_key})"
                )
                return {
                    "status": "accepted",
                    "message": f"Webhook received but no secret configured for {solution_type.value}",
                    "timestamp": datetime.now().isoformat(),
                }

        # Verify the notion_page_id format
        try:
            if hasattr(manual_service, "_format_page_id"):
                formatted_page_id = manual_service._format_page_id(notion_page_id)
                logger.info(f"Formatted page ID: {formatted_page_id}")
        except ValueError as e:
            return {
                "status": "accepted",
                "message": f"Invalid Notion page ID format: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

        # Check if this solution is configured
        if solution_type not in manual_service.root_page_ids:
            return {
                "status": "accepted",
                "message": f"Solution {solution_type.value} is not configured with a root page ID",
                "timestamp": datetime.now().isoformat(),
            }

        # Get cached nodes for this solution
        cached_nodes = manual_service.manuals_cache.get(solution_type, [])

        # Check if the page belongs to this solution
        def find_page_in_nodes(nodes, target_id):
            for node in nodes:
                if hasattr(node, "object_id") and node.object_id == target_id:
                    return True
                if hasattr(node, "children") and node.children:
                    if find_page_in_nodes(node.children, target_id):
                        return True
            return False

        # Define the background task for cache update
        async def update_cache_and_notify():
            try:
                # The update_manuals_cache method already creates a notification,
                # but we want to add node info for document update notifications.
                await manual_service.update_manuals_cache(solution_type, notion_page_id)

                # After cache update, add a document update notification with node info
                full_title_path = manual_service.get_full_title_path(
                    notion_page_id, solution_type
                )
                message = (
                    f"{full_title_path} page is updated"
                    if full_title_path
                    else f"Document {notion_page_id} was updated via webhook."
                )

                # Extract last_edited_by and last_edited_time from the refreshed cache
                last_edited_by = None
                last_edited_time = None
                nodes = manual_service.manuals_cache.get(solution_type, [])

                def find_node(nodes, target_id):
                    for node in nodes:
                        if hasattr(node, "object_id") and node.object_id == target_id:
                            return node
                        if hasattr(node, "children") and node.children:
                            found = find_node(node.children, target_id)
                            if found:
                                return found
                    return None

                updated_node = find_node(nodes, notion_page_id)
                if updated_node:
                    last_edited_by = getattr(updated_node, "last_edited_by", None)
                    last_edited_time = getattr(updated_node, "last_edited_time", None)

                manual_service._add_notification(
                    status=NotificationStatus.INFO,
                    title=f"{solution_type.value.upper()} Document Updated",
                    message=message,
                    solution=solution_type,
                    notification_type=NotificationSourceType.DOCUMENT_UPDATE,
                    node={
                        "notion_page_id": notion_page_id,
                        "parent_id": webhook_event.data.parent.id
                        if webhook_event.data and webhook_event.data.parent
                        else None,
                        "last_edited_by": last_edited_by,
                        "last_edited_time": last_edited_time.isoformat()
                        if last_edited_time
                        else None,
                    },
                )
            except Exception as e:
                logger.error(
                    f"Background task error - updating cache for {solution_type.value}: {str(e)}"
                )
                # Add error notification only on failure
                manual_service._add_notification(
                    status=NotificationStatus.ERROR,
                    title=f"{solution_type.value.upper()} Update Failed",
                    message=f"Failed to update document in {solution_type.value.upper()}: {str(e)}",
                    solution=solution_type,
                    notification_type=NotificationSourceType.DOCUMENT_UPDATE,
                )

        # If the page is found in cache or cache is empty (first time), schedule the update
        if not cached_nodes or find_page_in_nodes(cached_nodes, notion_page_id):
            logger.info(
                f"Page {notion_page_id} belongs to solution {solution_type.value}, scheduling cache update"
            )
            background_tasks.add_task(update_cache_and_notify)

            return {
                "status": "accepted",
                "message": f"Cache update scheduled for page {notion_page_id} in solution: {solution_type.value}",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            # Page doesn't belong to this solution, but still return 200
            return {
                "status": "accepted",
                "message": f"Page {notion_page_id} does not belong to solution {solution_type.value}",
                "timestamp": datetime.now().isoformat(),
            }

    except HTTPException:
        # Re-raise HTTP exceptions for authentication/signature validation failures
        raise
    except Exception as e:
        logger.error(
            f"Error processing Notion webhook for {solution_type.value}: {str(e)}"
        )
        return {
            "status": "accepted",
            "message": "Webhook received but encountered unexpected error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@router.post(
    "/webhook/notion/zcp", include_in_schema=True, openapi_extra={"security": []}
)
async def notion_webhook_zcp(
    request: Request,
    background_tasks: BackgroundTasks,
    manual_service: ManualService = Depends(get_manual_service),
    x_notion_signature: Optional[str] = Header(None, alias="x-notion-signature"),
):
    """Webhook endpoint for Notion to trigger when any ZCP page is updated."""
    return await process_notion_webhook(
        request, SolutionType.ZCP, manual_service, background_tasks, x_notion_signature
    )


@router.post(
    "/webhook/notion/apim", include_in_schema=True, openapi_extra={"security": []}
)
async def notion_webhook_apim(
    request: Request,
    background_tasks: BackgroundTasks,
    manual_service: ManualService = Depends(get_manual_service),
    x_notion_signature: Optional[str] = Header(None, alias="x-notion-signature"),
):
    """Webhook endpoint for Notion to trigger when any APIM page is updated."""
    return await process_notion_webhook(
        request, SolutionType.APIM, manual_service, background_tasks, x_notion_signature
    )


@router.post(
    "/webhook/notion/amdp", include_in_schema=True, openapi_extra={"security": []}
)
async def notion_webhook_amdp(
    request: Request,
    background_tasks: BackgroundTasks,
    manual_service: ManualService = Depends(get_manual_service),
    x_notion_signature: Optional[str] = Header(None, alias="x-notion-signature"),
):
    """Webhook endpoint for Notion to trigger when any AMDP page is updated."""
    return await process_notion_webhook(
        request, SolutionType.AMDP, manual_service, background_tasks, x_notion_signature
    )
