from pydantic import BaseModel
from typing import List

class Team(BaseModel):
    id: int
    name: str

class SaveMatchupsRequest(BaseModel):
    tournament_id: str
    round: str  # e.g., "qualifiers", "semifinals", "final"
    matchups: List[List[Team]]

class GetMatchupsResponse(BaseModel):
    tournament_id: str
    round: str
    matchups: List[List[Team]]
