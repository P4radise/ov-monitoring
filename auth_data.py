from dataclasses import dataclass

@dataclass
class OnevizionAuth:
    url: str
    access_key: str
    secret_key: str
    is_token_auth: bool = True


@dataclass
class AwsAuth:
    access_key_id: str
    secret_access_key: str
    region: str