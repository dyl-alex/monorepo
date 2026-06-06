import hashlib
import json
import math
from datetime import datetime

from db import get_connection


def sanitize_json_value(value):
    if isinstance(value, dict):
        return {key: sanitize_json_value(item) for key, item in value.items()}

    if isinstance(value, list):
        return [sanitize_json_value(item) for item in value]

    if isinstance(value, tuple):
        return [sanitize_json_value(item) for item in value]

    if isinstance(value, float) and not math.isfinite(value):
        return None

    return value


def jsonb_dumps(value, *, sort_keys: bool = True) -> str:
    return json.dumps(
        sanitize_json_value(value),
        sort_keys=sort_keys,
        separators=(",", ":"),
        default=str,
        allow_nan=False,
    )


def _response_hash(endpoint_name: str, endpoint_params: dict, response_json) -> str:
    payload = {
        "endpoint_name": endpoint_name,
        "endpoint_params": endpoint_params,
        "response_json": response_json,
    }
    return hashlib.sha256(jsonb_dumps(payload).encode("utf-8")).hexdigest()


def store_raw_api_response(
    *,
    endpoint_name: str,
    endpoint_params: dict,
    response_json,
    season_id: str | None = None,
    game_id: str | None = None,
    player_id: int | None = None,
    team_id: int | None = None,
) -> None:
    response_hash = _response_hash(endpoint_name, endpoint_params, response_json)

    sql = """
    insert into public.raw_api_responses (
      endpoint_name,
      endpoint_params,
      response_json,
      response_hash,
      season_id,
      game_id,
      player_id,
      team_id,
      fetched_at
    )
    values (
      %(endpoint_name)s,
      %(endpoint_params)s::jsonb,
      %(response_json)s::jsonb,
      %(response_hash)s,
      %(season_id)s,
      %(game_id)s,
      %(player_id)s,
      %(team_id)s,
      %(fetched_at)s
    )
    on conflict (endpoint_name, response_hash)
    do update set
      endpoint_params = excluded.endpoint_params,
      response_json = excluded.response_json,
      season_id = excluded.season_id,
      game_id = excluded.game_id,
      player_id = excluded.player_id,
      team_id = excluded.team_id,
      fetched_at = excluded.fetched_at;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                {
                    "endpoint_name": endpoint_name,
                    "endpoint_params": jsonb_dumps(endpoint_params),
                    "response_json": jsonb_dumps(response_json),
                    "response_hash": response_hash,
                    "season_id": season_id,
                    "game_id": game_id,
                    "player_id": player_id,
                    "team_id": team_id,
                    "fetched_at": datetime.utcnow(),
                },
            )
        conn.commit()
