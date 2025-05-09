from fastapi import APIRouter, HTTPException, Query
from schemas.tournament import SaveMatchupsRequest
from schemas.match import MatchResult, MatchResults
from database import database
import uuid

router = APIRouter()

def get_tournaments_collection():
    return database["tournaments"]

@router.post("/tournament/matchups")
async def save_matchups(data: SaveMatchupsRequest):
    tournaments = get_tournaments_collection()
    matches_col = database["matches"]
    rounds = ["quarterfinal", "semifinal", "final"]
    matchups_dict = {}
    match_id_counter = 1
    for rnd in rounds:
        if rnd == data.round:
            matchups_dict[rnd] = []
            for pair in data.matchups:
                match_id = str(uuid.uuid4())
                match_pair = []
                for team in pair:
                    if team is not None:
                        team_dict = team.dict()
                        match_pair.append(team_dict)
                    else:
                        match_pair.append(None)
                # Attach match_id to the pair (not to each team)
                matchups_dict[rnd].append({"match_id": match_id, "teams": match_pair})
                # Create a match document for each match in this round with all required fields
                match_doc = {
                    "id": match_id_counter,
                    "match_id": match_id,
                    "teamA": match_pair[0],
                    "teamB": match_pair[1],
                    "round": rnd,
                    "status": "pending",
                    "currentRound": 1,
                    "currentPhase": "waiting_for_defender",
                    "results": {
                        "round1": {"attacker": "", "defender": "", "attackerFoundKey": None, "attackerTime": None, "defenderPromptLength": None, "secretKey": None},
                        "round2": {"attacker": "", "defender": "", "attackerFoundKey": None, "attackerTime": None, "defenderPromptLength": None, "secretKey": None}
                    },
                    "winner": None,
                    "tournament_id": data.tournament_id
                }
                await matches_col.insert_one(match_doc)
                match_id_counter += 1
        else:
            num_matches = 4 if rnd == "quarterfinal" else 2 if rnd == "semifinal" else 1
            matchups_dict[rnd] = [
                {"match_id": str(uuid.uuid4()), "teams": [None, None]}
                for _ in range(num_matches)
            ]
    await tournaments.update_one(
        {"tournament_id": data.tournament_id},
        {"$set": {f"matchups": matchups_dict}},
        upsert=True
    )
    return {"success": True, "message": f"Matchups for {data.round} saved (all rounds initialized)", "tournament_id": data.tournament_id, "round": data.round}

@router.get("/tournament/matchups")
async def get_matchups(tournament_id: str = Query(...), round: str = Query(...)):
    tournaments = get_tournaments_collection()
    doc = await tournaments.find_one({"tournament_id": tournament_id})
    if not doc or "matchups" not in doc or round not in doc["matchups"]:
        raise HTTPException(status_code=404, detail="Matchups not found for this round")
    return {"tournament_id": tournament_id, "round": round, "matchups": doc["matchups"][round]}
