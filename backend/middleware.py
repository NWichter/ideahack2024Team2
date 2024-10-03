from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from utils.auth import verify_jwt


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                # Extract and verify the JWT token
                token = auth_header.split(" ")[1]
                verify_jwt(token)
            except Exception as _:
                raise HTTPException(
                    status_code=401, detail="Invalid or missing credentials"
                )
        else:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        # Proceed to the next request handler
        response = await call_next(request)
        return response
