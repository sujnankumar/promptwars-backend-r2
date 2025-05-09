from pydantic import BaseModel
from typing import List

class LoginRequest(BaseModel):
    username: str
    password: str
    role: str  # 'admin' or 'team'

class LoginResponse(BaseModel):
    success: bool
    role: str
    token: str

class RegisterAdminRequest(BaseModel):
    username: str
    password: str

class RegisterTeamRequest(BaseModel):
    team_name: str
    password: str

class RegisterTeamsBulkRequest(BaseModel):
    team_names: List[str]
