import json
from datetime import datetime
from typing import Any

from db import get_connection


def start_ingestion_run(
    *,
    job_name: str,
    season_id: str | None = None,
    season_type: str | None = None,
    target_date: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> int:
    sql = """
    insert into public.ingestion_runs (
      job_name,
      status,
      season_id,
      season_type,
      target_date,
      metadata
    )
    values (
      %(job_name)s,
      'started',
      %(season_id)s,
      %(season_type)s,
      %(target_date)s,
      %(metadata)s::jsonb
    )
    returning id;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                {
                    "job_name": job_name,
                    "season_id": season_id,
                    "season_type": season_type,
                    "target_date": target_date,
                    "metadata": json.dumps(metadata or {}),
                },
            )
            run_id = cur.fetchone()[0]
        conn.commit()

    return int(run_id)


def finish_ingestion_run(
    *,
    run_id: int,
    status: str,
    rows_inserted: int = 0,
    rows_updated: int = 0,
    rows_failed: int = 0,
    error_message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    sql = """
    update public.ingestion_runs
    set
      status = %(status)s,
      finished_at = %(finished_at)s,
      rows_inserted = %(rows_inserted)s,
      rows_updated = %(rows_updated)s,
      rows_failed = %(rows_failed)s,
      error_message = %(error_message)s,
      metadata = coalesce(metadata, '{}'::jsonb) || %(metadata)s::jsonb
    where id = %(run_id)s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                {
                    "run_id": run_id,
                    "status": status,
                    "finished_at": datetime.utcnow(),
                    "rows_inserted": rows_inserted,
                    "rows_updated": rows_updated,
                    "rows_failed": rows_failed,
                    "error_message": error_message,
                    "metadata": json.dumps(metadata or {}),
                },
            )
        conn.commit()
