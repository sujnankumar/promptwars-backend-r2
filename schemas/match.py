from pydantic import BaseModel
from typing import Optional

class Team(BaseModel):
    id: int
    name: str

class MatchPhase(str):
    WAITING_FOR_DEFENDER = "waiting_for_defender"
    DEFENDER_SETUP = "defender_setup"
    ATTACKER_CHAT = "attacker_chat"
    ROUND_COMPLETE = "round_complete"
    WAITING_FOR_ROLE_SWAP = "waiting_for_role_swap"
    MATCH_COMPLETE = "match_complete"

class MatchResult(BaseModel):
    attacker: str
    defender: str
    attackerFoundKey: Optional[bool] = None
    attackerTime: Optional[int] = None
    defenderPromptLength: Optional[int] = None
    secretKey: Optional[str] = None

class MatchResults(BaseModel):
    round1: MatchResult
    round2: MatchResult

class Match(BaseModel):
    id: int
    teamA: Optional[Team]
    teamB: Optional[Team]
    round: str
    status: str
    currentRound: int
    currentPhase: str
    results: MatchResults
    winner: Optional[str] = None
