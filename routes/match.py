from fastapi import APIRouter, HTTPException, Query, Body
from schemas.match import Match, MatchPhase, MatchResults
from database import database
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter()

def get_matches_collection():
    return database["matches"]

@router.get("/matches", response_model=List[Match])
async def list_matches(tournament_id: str = Query(...)):
    matches_col = get_matches_collection()
    matches_cursor = matches_col.find({"tournament_id": tournament_id})
    matches = []
    async for match in matches_cursor:
        match["id"] = match.get("id")
        match.pop("_id", None)
        if "phaseStartTime" not in match:
            match["phaseStartTime"] = None
        matches.append(match)
    return matches

@router.get("/matches/{match_id}", response_model=Match)
async def get_match(match_id: int, tournament_id: str = Query(...)):
    matches_col = get_matches_collection()
    match = await matches_col.find_one({"id": match_id, "tournament_id": tournament_id})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.pop("_id", None)
    if "phaseStartTime" not in match:
        match["phaseStartTime"] = None
    return match

@router.get("/matches/for_team", response_model=Match)
async def get_match_for_team(tournament_id: str = Query(...), team_name: str = Query(...)):
    matches_col = get_matches_collection()
    match = await matches_col.find_one({
        "tournament_id": tournament_id,
        "$or": [{"teamA.name": team_name}, {"teamB.name": team_name}]
    })
    if not match:
        raise HTTPException(status_code=404, detail="No match found for this team")
    match.pop("_id", None)
    return match

@router.get("/matches/by_team", response_model=List[Match])
async def get_matches_by_team(tournament_id: str = Query(...), team_name: str = Query(...)):
    matches_col = get_matches_collection()
    matches_cursor = matches_col.find({
        "tournament_id": tournament_id,
        "$or": [{"teamA.name": team_name}, {"teamB.name": team_name}]
    })
    matches = []
    async for match in matches_cursor:
        match.pop("_id", None)
        matches.append(match)
    return matches

@router.post("/matches")
async def save_matches(tournament_id: str, matches: List[Match]):
    matches_col = get_matches_collection()
    # Remove old matches for this tournament
    await matches_col.delete_many({"tournament_id": tournament_id})
    # Insert new matches
    docs = [dict(m) | {"tournament_id": tournament_id} for m in matches]
    await matches_col.insert_many(docs)
    return {"success": True, "message": f"{len(matches)} matches saved", "tournament_id": tournament_id}

@router.patch("/matches/{match_id}")
async def update_match(match_id: int, match: Match, tournament_id: str):
    matches_col = get_matches_collection()
    result = await matches_col.update_one(
        {"id": match_id, "tournament_id": tournament_id},
        {"$set": match.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"success": True, "message": "Match updated"}

@router.patch("/matches/{match_id}/phase")
async def update_match_phase(
    match_id: int,
    tournament_id: str,
    phase: str = Body(..., embed=True),
    current_round: int = Body(..., embed=True)
):
    matches_col = get_matches_collection()
    now = datetime.utcnow().timestamp()
    result = await matches_col.update_one(
        {"id": match_id, "tournament_id": tournament_id},
        {"$set": {"currentPhase": phase, "currentRound": current_round, "phaseStartTime": now}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"success": True, "message": "Phase updated", "phaseStartTime": now}

@router.patch("/matches/{match_id}/results")
async def update_match_results(
    match_id: int,
    tournament_id: str,
    results: Dict[str, Any] = Body(..., embed=True)
):
    matches_col = get_matches_collection()
    result = await matches_col.update_one(
        {"id": match_id, "tournament_id": tournament_id},
        {"$set": {"results": results}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"success": True, "message": "Results updated"}

@router.post("/matches/{match_id}/finalize")
async def finalize_match(
    match_id: int,
    tournament_id: str,
):
    matches_col = get_matches_collection()
    match = await matches_col.find_one({"id": match_id, "tournament_id": tournament_id})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    results = match.get("results", {})
    winner = compute_winner(results, match)
    await matches_col.update_one(
        {"id": match_id, "tournament_id": tournament_id},
        {"$set": {"currentPhase": "match_complete", "winner": winner}}
    )
    return {"success": True, "winner": winner}

def compute_winner(results: dict, match: dict) -> str:
    r1 = results.get("round1", {})
    r2 = results.get("round2", {})
    if r1.get("attackerFoundKey") and r2.get("attackerFoundKey"):
        if (r1.get("attackerTime", float("inf")) < r2.get("attackerTime", float("inf"))):
            return r1.get("attacker", "")
        else:
            return r2.get("attacker", "")
    elif r1.get("attackerFoundKey"):
        return r1.get("attacker", "")
    elif r2.get("attackerFoundKey"):
        return r2.get("attacker", "")
    else:
        d1 = r1.get("defenderPromptLength")
        d2 = r2.get("defenderPromptLength")
        d1 = d1 if d1 is not None else float("inf")
        d2 = d2 if d2 is not None else float("inf")
        if d1 < d2:
            return r1.get("defender", "")
        else:
            return r2.get("defender", "")
