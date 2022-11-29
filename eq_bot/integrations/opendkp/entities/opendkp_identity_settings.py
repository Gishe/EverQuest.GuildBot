from dataclasses import dataclass

@dataclass
class OpenDkpIdentitySettings:
    client_id: str
    cognito_user_pool: str
    cognito_client_id: str
    cognito_pool_id: str
