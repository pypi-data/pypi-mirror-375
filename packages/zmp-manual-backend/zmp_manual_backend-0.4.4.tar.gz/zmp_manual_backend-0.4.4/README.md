# ZMP Manual Backend

![Platform Badge](https://img.shields.io/badge/platform-zmp-red)
![Component Badge](https://img.shields.io/badge/component-manual_backend-red)
![CI Badge](https://img.shields.io/badge/ci-github_action-green)
![License Badge](https://img.shields.io/badge/license-MIT-green)

A high-performance backend service for managing manual content from Notion to Docusaurus. Supports real-time progress tracking, multiple language translations, and automated publishing workflows.

## Features

- Exports Notion pages to Markdown/MDX format
- Preserves document structure and formatting
- Supports multiple target languages simultaneously
- Real-time progress tracking with Server-Sent Events
- Automated translation integration
- User-specific notification system for export status
- Docusaurus-compatible output structure
- Job management and monitoring
- Secure authentication with JWT tokens

## API Endpoints

### Sidebar

```plaintext
GET /api/manual/v1/sidebar
- Get information about all available solutions
- Response: {"solutions": [{"name": "string", "solution_type": "string", "root_page_id": "string"}]}
```

### Manual Service

```plaintext
GET /api/manual/v1/manuals
- Get hierarchical list of manuals and folders
- Query param: selected_solution (zcp, apim, amdp)
- Response: List of nodes with object_id, title, is_directory, notion_url, and children

POST /api/manual/v1/publish
- Publish a manual by exporting from Notion and translating
- Request body: {
    "notion_page_id": "string",
    "selected_solution": "string",
    "target_languages": ["string"]
  }
- Response: {"job_id": "string"}

GET /api/manual/v1/watch/{job_id}
- Watch publication progress using Server-Sent Events
- Returns real-time status updates
- Includes periodic ping events to keep connection alive
- Connection closes automatically when job reaches terminal state

GET /api/manual/v1/jobs/{job_id}
- Get current status of a publication job
- Response includes job status, progress, and any error messages

GET /api/manual/v1/jobs
- List recent publication jobs
- Query params:
  - status: Filter by job status
  - limit: Number of jobs to return (1-100)
```

### Notifications

```plaintext
GET /api/manual/v1/notifications/stream
- Stream notifications in real-time using Server-Sent Events (SSE)
- Query params:
  - include_read: Include read notifications
- Returns: SSE stream with notification JSON data
- Includes periodic ping events to keep connection alive

POST /api/manual/v1/notifications/{notification_id}/read
- Mark a notification as read

POST /api/manual/v1/notifications/clear
- Clear all notifications for the authenticated user
```

### Notion Webhooks

```plaintext
POST /api/manual/v1/webhook/notion/zcp
POST /api/manual/v1/webhook/notion/apim
POST /api/manual/v1/webhook/notion/amdp
- Endpoint for Notion webhook events for each solution
- Requires x-notion-signature header for verification
- Automatically updates cache and notifies users of changes
- Handles page updates, creations, and deletions
```

### Authentication

```plaintext
GET /api/manual/v1/auth/docs/oauth2-redirect
- Keycloak OAuth2 callback for the redirect URI
```

## Environment Configuration

The application requires the following environment variables:

```plaintext
NOTION_TOKEN: Your Notion API token
ZCP_ROOT_PAGE_ID: Root page ID for ZCP documentation
APIM_ROOT_PAGE_ID: Root page ID for APIM documentation
AMDP_ROOT_PAGE_ID: Root page ID for AMDP documentation
REPO_BASE_PATH: Base path for repository data (default: ./repo)
SOURCE_DIR: Source directory for documentation (default: docs)
TARGET_DIR: Target directory for translations (default: i18n)
GITHUB_REPO_URL: URL of the GitHub repository
GITHUB_BRANCH: Branch to use (default: develop)
TARGET_LANGUAGES: Comma-separated list of target languages (default: ko,ja,zh)
CACHE_BASE_PATH: Base path for cache files (default: ./cache)
OPENAI_API_KEY: OpenAI API key for translations
OPENAI_MODEL: OpenAI model to use for translations
MAX_CHUNK_SIZE: Maximum chunk size for translations
MAX_CONCURRENT_REQUESTS: Maximum number of concurrent requests
```

## Cache System

The application implements a sophisticated caching system for manual content:

1. **In-Memory Cache**:
   - Maintains a cache of manual nodes in memory
   - Updated when content changes or is loaded from filesystem
   - Improves response time for frequent requests

2. **Filesystem Cache**:
   - Persists cache data to disk for durability
   - Supports both JSON and pickle formats
   - Automatically loads cache on startup
   - Updated when content changes

3. **Cache Structure**:
   - Organized by solution type (ZCP, APIM, AMDP)
   - Maintains parent-child relationships between nodes
   - Includes metadata like last edited time and author
   - Preserves document structure and hierarchy

4. **Cache Updates**:
   - Automatic updates via Notion webhooks
   - Manual refresh through API endpoints
   - Periodic cleanup of old cache files
   - Validation of cache integrity

## Real-Time Notifications with Server-Sent Events (SSE)

The system provides real-time notifications using Server-Sent Events (SSE), allowing clients to receive notifications as they happen without polling the server.

### SSE Notification Endpoint

```plaintext
GET /notifications/stream
```

This endpoint establishes a persistent connection with the client using SSE. The server will push notifications to the client as they are created.

**Query Parameters:**
- `include_read` (boolean, default: false): Whether to include notifications that have been marked as read.

**Authentication:**
- Requires a valid JWT token in the Authorization header.

**Response:**
- A stream of SSE events, each containing a JSON-serialized notification.
- Each notification event follows the format: `data: {...JSON notification data...}`
- Ping events are sent periodically with format: `data: ping` to keep the connection alive.
- Notification data includes document_title when available.

### SSE Watch Endpoint

```plaintext
GET /watch/{job_id}
```

This endpoint establishes a persistent connection using SSE to watch the progress of a specific job.

**Path Parameters:**
- `job_id`: The ID of the job to watch.

**Authentication:**
- Requires a valid JWT token in the Authorization header.

**Response:**
- A stream of SSE events with real-time job status updates.
- Initial event contains the current status of the job.
- Periodic ping events with format: `data: ping` to keep the connection alive.
- Status update events whenever the job status changes.
- Connection closes automatically when job reaches a terminal state (COMPLETED or FAILED).

### Client Implementation Examples

#### JavaScript Example

```javascript
// Create and configure EventSource for SSE
const token = "YOUR_JWT_TOKEN";
const eventSource = new EventSource("/notifications/stream", {
  headers: {
    "Authorization": `Bearer ${token}`
  }
});

// Handle incoming notifications
eventSource.onmessage = function(event) {
  const notification = JSON.parse(event.data);
  console.log("Received notification:", notification);
  // Handle notification (display in UI, etc.)
};

// Handle connection open
eventSource.onopen = function() {
  console.log("SSE connection established");
};

// Handle errors
eventSource.onerror = function(error) {
  console.error("SSE connection error:", error);
  // Optionally reconnect or report error to user
};

// Close connection when done
function closeConnection() {
  eventSource.close();
}
```

#### Python Example

```python
import asyncio
import aiohttp
import json

async def listen_for_notifications(token):
    headers = {"Authorization": f"Bearer {token}"}
    url = "http://localhost:8000/notifications/stream"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                print(f"Failed to connect: {response.status}")
                return

            async for line in response.content:
                line = line.decode('utf-8').strip()

                # Parse SSE format: "data: {json}"
                if line.startswith('data: '):
                    data = line[6:]  # Remove "data: " prefix
                    notification = json.loads(data)
                    # Handle notification
                    print(f"New notification: {notification['title']}")
```

### Best Practices for SSE Usage

1. **Always close the connection** when a client no longer needs notifications to free up server resources.
2. **Implement error handling and reconnection logic** in client applications to maintain stable connections.
3. **Use the query parameters** to filter notifications appropriately and reduce unnecessary network traffic.
4. **Consider implementing a maximum connection time** for long-lived connections to prevent resource exhaustion.

## Deployment Guide

### Recent Updates and Improvements

The application has been updated with several improvements:

1. **Storage Configuration**:
   - Added separate persistent storage for manuals cache using EFS (`efs-zcp-retain` storage class)
   - Repository data uses EBS (`ebs-gp3` storage class) for better performance
   - Improved volume configuration in Helm charts for better persistence
   - Added `CACHE_BASE_PATH` to separate cache files from repository data

2. **GitHub Integration**:
   - Added `GITHUB_BRANCH` parameter to specify which branch to use (defaults to "develop")
   - Updated code to properly handle the branch parameter throughout the application
   - Fixed references to the branch in logging and error messages
   - Modified Git credential handling for better security

3. **Cache System Improvements**:
   - Implemented two-level caching (memory and filesystem)
   - Added support for both JSON and pickle cache formats
   - Improved cache validation and integrity checks
   - Added automatic cache cleanup for old files
   - Enhanced cache update mechanism via webhooks

4. **Notion Integration**:
   - Added support for multiple solution types (ZCP, APIM, AMDP)
   - Implemented webhook endpoints for each solution
   - Added signature verification for webhook requests
   - Improved handling of page updates and deletions
   - Enhanced error handling and logging

5. **Performance Optimizations**:
   - Implemented concurrent request handling
   - Added configurable chunk size for translations
   - Improved memory usage with better data structures
   - Enhanced error recovery and retry mechanisms
   - Added request rate limiting and throttling

6. **Security Enhancements**:
   - Added JWT token validation
   - Implemented webhook signature verification
   - Enhanced error handling and logging
   - Added request validation and sanitization
   - Improved environment variable handling

### Deployment Steps

1. **Environment Setup**:
   ```bash
   # Required environment variables
   export NOTION_TOKEN="your_notion_token"
   export ZCP_ROOT_PAGE_ID="your_zcp_root_page_id"
   export APIM_ROOT_PAGE_ID="your_apim_root_page_id"
   export AMDP_ROOT_PAGE_ID="your_amdp_root_page_id"
   export GITHUB_REPO_URL="your_github_repo_url"
   export OPENAI_API_KEY="your_openai_api_key"
   ```

2. **Storage Configuration**:
   - Create EFS volume for cache storage
   - Create EBS volume for repository data
   - Configure storage classes in Kubernetes

3. **Kubernetes Deployment**:
   ```bash
   # Deploy using Helm
   helm install zmp-manual-backend ./k8s/helm \
     --set notion.token=$NOTION_TOKEN \
     --set notion.zcpRootPageId=$ZCP_ROOT_PAGE_ID \
     --set notion.apimRootPageId=$APIM_ROOT_PAGE_ID \
     --set notion.amdpRootPageId=$AMDP_ROOT_PAGE_ID \
     --set github.repoUrl=$GITHUB_REPO_URL \
     --set github.branch=develop \
     --set openai.apiKey=$OPENAI_API_KEY
   ```

4. **Verify Deployment**:
   ```bash
   # Check pod status
   kubectl get pods -l app=zmp-manual-backend

   # Check logs
   kubectl logs -l app=zmp-manual-backend

   # Check services
   kubectl get svc -l app=zmp-manual-backend
   ```

5. **Configure Webhooks**:
   - Set up Notion webhooks for each solution
   - Configure webhook URLs in Notion
   - Verify webhook signatures

6. **Monitor and Maintain**:
   - Monitor cache usage and cleanup
   - Check webhook delivery status
   - Review error logs and notifications
   - Perform regular backups of cache data

### Troubleshooting

1. **Cache Issues**:
   - Check cache directory permissions
   - Verify cache file integrity
   - Monitor cache size and cleanup
   - Check cache update logs

2. **Webhook Problems**:
   - Verify webhook signatures
   - Check webhook delivery status
   - Review webhook event logs
   - Test webhook endpoints

3. **Performance Issues**:
   - Monitor memory usage
   - Check concurrent request limits
   - Review translation chunk sizes
   - Analyze response times

4. **Storage Problems**:
   - Verify volume mounts
   - Check storage class configuration
   - Monitor disk usage
   - Review storage logs

## Installation

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in your project root:

```env
# Notion Configuration
NOTION_TOKEN=your-notion-token-here
ZCP_ROOT_PAGE_ID=your-root-page-id
APIM_ROOT_PAGE_ID=your-apim-root-page-id
AMDP_ROOT_PAGE_ID=your-amdp-root-page-id

# Repository Configuration
REPO_BASE_PATH=./repo
CACHE_BASE_PATH=./cache
SOURCE_DIR=docs
TARGET_DIR=i18n
GITHUB_REPO_URL=your-github-repo-url
GITHUB_BRANCH=develop  # The branch to use in the GitHub repository (default: develop)

# Translation Configuration
TARGET_LANGUAGES=ko,ja,zh

# Authentication Configuration
JWT_SECRET_KEY=your-secret-key-keep-it-secure
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENABLE_KEYCLOAK=True
```

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Quick start using run.sh (recommended)
chmod +x run.sh  # Make script executable (first time only)
./run.sh        # Starts server on port 8001 with auto-reload and debug logging

# Manual server start options
poetry run uvicorn zmp_manual_backend.main:app --reload
poetry run uvicorn zmp_manual_backend.main:app --reload --host 0.0.0.0 --port 8001
```

The `run.sh` script automatically:
- Checks if port 8001 is in use and frees it if needed
- Starts the FastAPI server with:
  - Host: 0.0.0.0 (accessible from other machines)
  - Port: 8001
  - Auto-reload enabled
  - Debug logging enabled

## Authentication

The application uses JWT (JSON Web Tokens) for authentication. All API endpoints (except `/auth/login`) require a valid JWT token in the Authorization header.

The token contains information about the user, including:
- Username
- Roles
- Email
- Full name

This user information is used to filter certain resources, such as notifications, to ensure users only see content that is relevant to them.

## User-Specific Notifications

Notifications can be:
1. **System-wide**: Visible to all users (no user_id specified)
2. **User-specific**: Visible only to a specific user

When retrieving notifications through the `/notifications` or `/notifications/latest` endpoints, the system automatically filters the results based on the user's identity from the authentication token.

## Directory Structure

The service creates a Docusaurus-compatible directory structure:

```
repo/                  # Repository data (using EBS storage in Kubernetes)
├── docs/
│   └── [solution]/
│       └── content.mdx
└── i18n/
    ├── ko/
    │   └── docusaurus-plugin-content-docs/
    │       └── current/
    │           └── [solution]/
    │               └── content.mdx
    ├── ja/
    │   └── ...
    └── zh/
        └── ...

cache/                # Cache data (using EFS storage in Kubernetes)
└── manuals/
    ├── zcp_manuals.json
    ├── apim_manuals.json
    └── amdp_manuals.json
```

## Job States

Publication jobs follow a specific workflow with the following states:

| State | Description |
|-------|-------------|
| STARTED | Job has been initiated |
| CHECKING_REPO | Verifying repository access and status |
| CLONING | Cloning the repository if not exists |
| PULLING | Pulling latest changes from repository |
| EXPORTING | Exporting content from Notion |
| EXPORT_COMMIT | Committing exported content |
| TRANSLATING | Translating content to target languages |
| TRANSLATION_COMMIT | Committing translated content |
| PUSHING | Pushing changes to repository |
| COMPLETED | Successfully finished |
| FAILED | Failed to complete |

### Failure Reasons

When a job fails, it can have one of these specific failure reasons:

| Reason | Description |
|--------|-------------|
| REPO_ACCESS | Failed to access or authenticate with the repository |
| EXPORT_FAILED | Failed to export content from Notion |
| TRANSLATION_FAILED | Failed during content translation |
| GIT_OPERATION_FAILED | Failed during a git operation |

## Notification Types

The service provides three types of notifications:

| Type | Description |
|------|-------------|
| SUCCESS | Successful operation notifications |
| ERROR | Error and failure notifications |
| INFO | General information notifications |
| PROCESSING | In-progress operation notifications |

Each notification includes:
- Unique ID
- Type (success/error/info/processing)
- Title
- Message
- Associated solution (optional)
- User ID (optional, for user-specific notifications)
- Creation timestamp
- Read status

## Solution Types

The service supports the following solution types:

| Type | Description |
|------|-------------|
| ZCP | Cloud Z CP Documentation |
| APIM | API Management Documentation |
| AMDP | Application Modernization Documentation |

## Supported Languages

The following language codes are supported:

| Code | Language    |
|------|------------|
| ko   | Korean     |
| fr   | French     |
| ja   | Japanese   |
| es   | Spanish    |
| de   | German     |
| zh   | Chinese    |
| ru   | Russian    |
| it   | Italian    |
| pt   | Portuguese |
| ar   | Arabic     |

## License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Docker Deployment

For detailed instructions on building a Docker image and deploying to a Kubernetes cluster, see the [Kubernetes Deployment Guide](k8s/README_DEPLOYMENT.md).

Quick start:

1. Build and push the Docker image:
   ```bash
   ./k8s/build-and-push.sh
   ```

2. Deploy the application:
   ```bash
   ./k8s/deploy-app.sh
   ```
