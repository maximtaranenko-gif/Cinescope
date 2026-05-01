from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from api.api_manager import ApiManager
from constants import Roles
from models.user_models import LoginRequest


class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    email: str
    password: str
    roles: List[Roles]
    api: ApiManager
    id: Optional[str] = None

    @property
    def creds(self) -> LoginRequest:
        return LoginRequest(email=self.email, password=self.password)