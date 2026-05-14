from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import get_team_key_info

security = HTTPBearer(auto_error=False)


async def verify_team_key(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")

    token = credentials.credentials
    info = get_team_key_info(token)
    if not info:
        raise HTTPException(status_code=401, detail="Invalid team API key")

    user = info.get("user", "unknown")
    request.state.user = user
    request.state.team_key = token
    return user
