# greeting-cards — Claude Context

## Project Purpose
A personal household tool for managing greeting card logistics. Tracks households,
mailing addresses, events (holidays, birthdays, baby showers, etc.), gifts received,
and cards sent. Answers the question: "Who needs a card, and where do I send it?"

This is a **local-only, personal-use app** — it will never be public-facing. Some
architectural shortcuts are intentional (see Known Quirks below).

## Companion Repos
- **This repo** (`brystmar/greeting-cards`): Python/Flask backend
- **Frontend** (`brystmar/greeting-cards-ui`): React 19 + Vite UI

## Stack
| Layer | Technology |
|---|---|
| Language | Python |
| Framework | Flask + Flask-RESTful |
| ORM | Flask-SQLAlchemy |
| Database | PostgreSQL (`cards` = prod, `cards-dev` = dev) |
| Migrations | Alembic via Flask-Migrate |
| Deployment | Docker + Portainer stack on NUC 13i5 |
| IDE | PyCharm Professional |

## Repo Structure
```
greeting-cards/
├── main.py              # Entrypoint: initializes app, registers all API routes
├── root_logger.py       # Logging setup — must be initialized first in main.py
├── requirements.txt
├── Dockerfile
├── alembic.ini
├── backend/
│   ├── __init__.py      # create_app() factory, db init
│   └── config.py        # Config class: reads .env, sets DB connection, ports, etc.
├── models/
│   └── models.py        # All SQLAlchemy models
├── routes/              # One Flask-RESTful resource file per model
│   ├── address.py
│   ├── household.py
│   ├── event.py
│   ├── gift.py
│   ├── card.py
│   └── picklists.py
├── helpers/
│   └── helpers.py       # Utility functions incl. convert_to_bool()
└── migrations/          # Alembic migration files
```

## Data Models (`models/models.py`)
All models share: auto-increment integer PK, `created_date` + `last_modified`
timestamps (UTC), `notes` field, `to_dict()` method, `__repr__()`.

| Model | Table | Key Fields |
|---|---|---|
| `Address` | `address` | `household_id` (FK), `line_1/2`, `city`, `state`, `zip`, `country`, `full_address`, `is_current`, `is_likely_to_change`, `mail_the_card_to_this_address` |
| `Household` | `household` | `nickname` (unique index), `first_names`, `surname`, `address_to`, `formal_name`, `known_from`, `relationship`, `relationship_type`, `family_side`, `kids`, `pets`, `should_receive_holiday_card`, `is_relevant` |
| `Event` | `event` | `name`, `date`, `year`, `is_archived` |
| `Gift` | `gift` | `event_id` (FK), `household_id`, `description`, `type`, `origin`, `should_a_card_be_sent` |
| `Card` | `card` | `type`, `gift_id` (FK), `event_id` (FK), `household_id` (FK), `address_id` (FK), `date_sent`, `was_returned` |
| `Picklists` | `picklist_values` | `household_relationship`, `household_relationship_type`, `household_family_side`, `card_type` (all comma-separated strings, split in `to_dict()`) |

## API Endpoints
All routes use `/api/v1/` prefix.

| Endpoint | Resource |
|---|---|
| `/api/v1/address` + `/api/v1/all_addresses` | Address |
| `/api/v1/household` + `/api/v1/all_households` | Household |
| `/api/v1/event` + `/api/v1/all_events` | Event |
| `/api/v1/gift` + `/api/v1/all_gifts` | Gift |
| `/api/v1/card` + `/api/v1/all_cards` | Card |
| `/api/v1/picklist_values` | Picklists |

## Config & Environment
`backend/config.py` reads from `.env` via `env_tools`. Detects PyCharm path to apply
local env automatically. Key env vars:
- `POSTGRES_DB_CONNECTION` — prod DB URI
- `POSTGRES_DB_CONNECTION_DEV` — dev DB URI
- `USE_PROD_DATABASE` — "True" connects to prod (defaults to dev)
- `HOST_ADDRESS`, `BACKEND_PORT` (default 5001), `DEBUG_ENABLED`, `SECRET_KEY`

## Database Workflow
```bash
# Refresh dev DB from prod snapshot
pg_dump cards | psql cards-dev

# Run migrations
flask db upgrade
```

## Running Locally
```bash
python main.py
# Runs at http://localhost:5001
```

## Coding Conventions
- Logger initialized **before all other imports** in `main.py`
- All boolean fields stored as strings in DB; converted via `convert_to_bool()` on read
- All models include `created_date` and `last_modified` with UTC defaults
- CORS is fully open — intentional, local-only app
- 1NF compliance explicitly deprioritized — acknowledged in code comments

## Known Quirks / Technical Debt
- Boolean fields stored as strings — intentional shortcut
- `kids` and `pets` on `Household` are plain strings, not related tables
- `Picklists.__init__` references `self.is_default` which has no declared column — latent bug
- Non-US address support handled via `full_address` workaround field
