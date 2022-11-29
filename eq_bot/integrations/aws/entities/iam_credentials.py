from datetime import datetime
from dataclasses import dataclass

@dataclass
class IamCredentials:
    access_key_id: str
    secret_key: str
    session_token: str
    expires_at: datetime
