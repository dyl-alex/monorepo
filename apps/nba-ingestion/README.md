## Running The Ingestion App

The ingestion app should be run from:

```txt
apps/nba-ingestion/src
```

Before running commands, ensure:

1. Local Supabase is running
2. The Python virtual environment is activated
3. Dependencies are installed
4. `.env` exists and contains a valid `DATABASE_URL`

---

### 1. Start local Supabase

From the monorepo root:

```bash
supabase start
```

Or:

```bash
pnpm supabase:start
```

Verify the local database is running before continuing.

---

### 2. Navigate to the ingestion app

From the monorepo root:

```bash
cd apps/nba-ingestion
```

---

### 3. Create the virtual environment (first time only)

```bash
python -m venv .venv
```

---

### 4. Activate the virtual environment

#### PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

#### CMD

```cmd
.venv\Scripts\activate.bat
```

#### Git Bash / WSL / Linux / macOS

```bash
source .venv/bin/activate
```

When activated successfully, your terminal should look similar to:

```txt
(.venv) PS C:\Projects\monorepo\apps\nba-ingestion>
```

---

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 6. Create `.env` (first time only)

#### PowerShell

```powershell
Copy-Item .env.example .env
```

#### Bash

```bash
cp .env.example .env
```

Ensure the file contains:

```env
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres
LOG_LEVEL=INFO
NBA_SEASON=2024-25
NBA_SEASON_TYPE=Regular Season
```

---

### 7. Navigate to `src`

```bash
cd src
```

Commands should be executed from this folder.

---

## Example Commands

### Sync teams

```bash
python -m main sync-teams
```

---

### Sync players

```bash
python -m main sync-players
```

---

### Sync games for a season

```bash
python -m main sync-games --season 2024-25
```

---

### Sync player game stats

```bash
python -m main sync-player-game-stats --season 2024-25
```

---

### Sync team game stats

```bash
python -m main sync-team-game-stats --season 2024-25
```

---

### Run daily sync

```bash
python -m main sync-daily
```

---

### Run full backfill

```bash
python -m main backfill --season 2024-25
```

---

## Verifying Data

Open Supabase Studio and verify records were inserted into tables such as:

```txt
public.teams
public.players
```

Or query directly:

```sql
select count(*) from public.teams;
select count(*) from public.players;
```

---

## Stopping The Virtual Environment

When finished:

```bash
deactivate
```