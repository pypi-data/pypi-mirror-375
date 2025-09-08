import json
import logging
import os
import sys

import requests

from fastapi import APIRouter, HTTPException, Request, status

# Import Keycloak functionality
try:
    from zmp_manual_backend.api.oauth2_keycloak import (
        KEYCLOAK_CLIENT_ID,
        KEYCLOAK_CLIENT_SECRET,
        KEYCLOAK_REDIRECT_URI,
        KEYCLOAK_TOKEN_ENDPOINT,
        KEYCLOAK_USER_ENDPOINT,
        HTTP_CLIENT_SSL_VERIFY,
    )
except ImportError:
    logger = logging.getLogger("appLogger")
    logger.error("Failed to import Keycloak functionality")
    raise ImportError("Keycloak authentication is required but not available")

logger = logging.getLogger("appLogger")

router = APIRouter()


def save_token_data(tokens, user_info=None):
    """Save token data to files in the user's home directory."""
    token_dir = os.path.expanduser("~/.zmp-tokens")
    os.makedirs(token_dir, exist_ok=True)

    # Save the full token response
    with open(os.path.join(token_dir, "token.json"), "w") as f:
        json.dump(
            {
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "token_type": tokens.get("token_type", "bearer"),
                "expires_in": tokens.get("expires_in"),
                "user_info": user_info,
            },
            f,
            indent=2,
        )

    # Save just the access token to a separate file
    with open(os.path.join(token_dir, "access_token.txt"), "w") as f:
        f.write(tokens.get("access_token", ""))

    # Save the bearer token format
    with open(os.path.join(token_dir, "bearer_token.txt"), "w") as f:
        f.write(f"Bearer {tokens.get('access_token', '')}")

    print(f"Token data saved to {token_dir}/")


@router.get(
    "/docs/oauth2-redirect", summary="Keycloak OAuth2 callback for the redirect URI"
)
def callback(request: Request, code: str):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": KEYCLOAK_REDIRECT_URI,
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    idp_response = requests.post(
        KEYCLOAK_TOKEN_ENDPOINT,
        data=data,
        headers=headers,
        verify=HTTP_CLIENT_SSL_VERIFY,
    )  # verify=False: because of the SKCC self-signed certificate

    if idp_response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")

    tokens = idp_response.json()

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    # id_token = tokens.get("id_token")

    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    idp_response = requests.get(
        KEYCLOAK_USER_ENDPOINT, headers=headers, verify=HTTP_CLIENT_SSL_VERIFY
    )  # verify=False: because of the SKCC self-signed certificate
    if idp_response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_info = idp_response.json()

    logger.debug(f"user_info: {user_info}")

    request.session["refresh_token"] = refresh_token
    request.session["user_info"] = user_info

    total_bytes = _get_size(request.session)

    if total_bytes > 4096:
        logger.debug(f"Total bytes: {total_bytes}")
        logger.warning(f"The session data size({total_bytes}) is over than 4kb.")
        raise HTTPException(status_code=401, detail="Invalid token")

    return tokens


def _get_size(obj, seen=None):
    """Recursively find the size of objects including nested objects."""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Mark as seen
    seen.add(obj_id)
    # Recursively add sizes of referred objects
    if isinstance(obj, dict):
        size += sum([_get_size(v, seen) for v in obj.values()])
        size += sum([_get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += _get_size(obj.__dict__, seen)
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([_get_size(i, seen) for i in obj])
    return size


async def get_token(request: Request):
    """Extract and validate the token from the Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.split("Bearer ")[1]

    # Do a basic token validation to ensure it's a proper JWT
    parts = token.split(".")
    if len(parts) != 3:
        logger.error(
            f"Invalid token format: token has {len(parts)} segments, expected 3"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token
