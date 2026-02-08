from typing import Optional, Any

class HTTPException(Exception):
    def __init__(self, status_code: int, message: str, detail: Optional[Any] = None):
        self.status_code = status_code
        self.message = message,
        self.detail = detail