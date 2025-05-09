from fastapi import APIRouter, HTTPException
from schemas.auth import (
    LoginRequest, LoginResponse, RegisterAdminRequest, RegisterTeamRequest, RegisterTeamsBulkRequest
)
from database import get_users_collection
from bson import ObjectId
from utils.jwt_handler import create_access_token

router = APIRouter()

@router.post("/auth/login", response_model=LoginResponse)
async def login(data: LoginRequest):
    users = get_users_collection()
    user = await users.find_one({"username": data.username, "role": data.role})
    if data.role == "admin":
        if user and user.get("password") == data.password:
            token = create_access_token({"sub": data.username, "role": "admin"})
            return {"success": True, "role": "admin", "token": token}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        if user and user.get("password") == data.password:
            token = create_access_token({"sub": data.username, "role": "team"})
            return {"success": True, "role": "team", "token": token}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/auth/register-admin")
async def register_admin(data: RegisterAdminRequest):
    users = get_users_collection()
    existing = await users.find_one({"username": data.username, "role": "admin"})
    if existing:
        raise HTTPException(status_code=400, detail="Admin already exists")
    await users.insert_one({"username": data.username, "password": data.password, "role": "admin"})
    return {"success": True, "message": "Admin registered"}

@router.post("/auth/register-team")
async def register_team(data: RegisterTeamRequest):
    users = get_users_collection()
    existing = await users.find_one({"username": data.team_name, "role": "team"})
    if existing:
        raise HTTPException(status_code=400, detail="Team already exists")
    await users.insert_one({"username": data.team_name, "password": data.password, "role": "team"})
    return {"success": True, "message": "Team registered"}

@router.post("/auth/register-teams-bulk")
async def register_teams_bulk(data: RegisterTeamsBulkRequest):
    users = get_users_collection()
    team_docs = []
    for name in data.team_names:
        existing = await users.find_one({"username": name, "role": "team"})
        if not existing:
            team_docs.append({"username": name, "password": "teampass", "role": "team"})
    if team_docs:
        await users.insert_many(team_docs)
    return {"success": True, "message": f"{len(team_docs)} teams registered"}
