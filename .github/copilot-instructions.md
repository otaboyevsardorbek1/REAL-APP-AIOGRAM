## Quick orientation

This repository contains multiple Aiogram-based Telegram bot projects and a simple web_app. The goal of this file is to give AI coding agents the immediate, practical context needed to be productive in this codebase.

Key entry points
- Top-level / main runners: `main.py`, `bot-new.py`, `server.py` (root). Check these for which bot is intended to run.
- Subproject runners: `aiogram-shop-bot/run.py`, `online-shop-bot-pro/main.py` or `run.py`, and `web_site/run.py` or `wsgi.py` for the web app.

Architecture & patterns (what you'll see and why)
- Multiple independent bot projects live in the same workspace (e.g. `aiogram-shop-bot/`, `online-shop-bot-pro/`). Edit and test within the relevant subfolder.
- Aiogram initialization often follows the same pattern: `loader.py` creates Bot, Dispatcher and storage. Example: `online-shop-bot-pro/loader.py` defines `bot`, `dp` and helper `get_db()` for SQL sessions.
- Handlers are grouped by role under `app/handlers/` (e.g. `aiogram-shop-bot/app/handlers/admin_private/` and `user_private/`). Add new handlers to these folders and register them where the Dispatcher is created (see the subproject `run.py` / `main.py`).
- Shared bot concerns are organized in `app/common/` (filters, middlewares). Example: `aiogram-shop-bot/app/common/filters.py` contains `ChatTypeFilter` and `IsAdminFilter`; `middlewares.py` shows a `UserMiddleware` that auto-creates or updates users in DB.
- Database code varies per subproject: look for `db/` packages (`online-shop-bot-pro/db`) and `app/database/` (aiogram-shop-bot). Follow existing `requests.py`, `models.py` conventions (simple SQL/SQLite usage, sometimes using SQLAlchemy session providers).

Project-specific conventions (important, not generic)
- Multiple `requirements.txt` files exist. Note a top-level typo: `requarments.txt` (misspelled). When adding dependencies, check subproject `requirements.txt` files too.
- Config objects are stored per-subproject in `config.py` (e.g. `aiogram-shop-bot/config.py`, `online-shop-bot-pro/config.py`). Use `from config import config` where present.
- Logging: some projects have a small logger package `looger/loger.py` — preserve its API when adding logs.
- DB session helper: many projects provide a `get_db()` generator (see `online-shop-bot-pro/loader.py`). Use it for short-lived DB sessions.

Developer workflows (discovered from tree)
- Run a bot locally: run the subproject's `run.py` or the top-level `main.py` used by that subproject. Example patterns:

```powershell
# from the repo root, pick the subproject folder
python aiogram-shop-bot/run.py
python online-shop-bot-pro/main.py
python main.py        # top-level runner (may start a specific bot)
```

- Web app: `web_site/` contains `Dockerfile` and `wsgi.py` — it is WSGI-compatible. To run locally, inspect `web_site/run.py` or use a WSGI server.
- Tests: there are pytest tests under `web_site/app/tests/` (e.g. `tests_main.py`). Run `pytest web_site/app/tests` to execute them.

Integration & cross-component notes
- Cross-cutting code (filters, middlewares, keyboards) is under `app/common/` or `keyboards/`. Reuse these modules rather than duplicating code between subprojects.
- Templates for the web app live in `web_site/app/template/` and can be used for demo HTML endpoints.

Examples to cite when making edits
- To add a filter: follow `aiogram-shop-bot/app/common/filters.py` (class-style aiogram Filter, async __call__ returning bool).
- To add a middleware: follow `aiogram-shop-bot/app/common/middlewares.py` (subclass BaseMiddleware; inspect how user creation / blocking is handled).
- DB session usage: `online-shop-bot-pro/loader.py` yields a SQLAlchemy session via `get_db()` — use the same pattern for new DB helpers.

When in doubt
- Run the specific subproject's runner (look for `run.py`, `main.py`, or `loader.py`) rather than editing multiple projects at once.
- Preserve existing config keys and logging API. If you add a new package, update the correct `requirements.txt` in that subfolder and note the top-level spelling (`requarments.txt`) so CI/scripts don't miss it.

What I did / where to check
- Created this file to capture the repository-specific patterns discovered in code. Key files referenced above: `online-shop-bot-pro/loader.py`, `aiogram-shop-bot/app/common/filters.py`, `aiogram-shop-bot/app/common/middlewares.py`, `web_site/` and subproject `requirements.txt` files.

If something is missing or you want more detail (registering handlers, exact run-step for a particular bot), tell me which subproject you care about and I will expand the instructions with exact lines and a small runnable checklist.
