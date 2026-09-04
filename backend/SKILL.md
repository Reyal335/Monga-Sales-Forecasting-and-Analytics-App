---
name: monga-backend-architecture
description: Use this whenever writing, structuring, reviewing, or extending any code in the Monga_Model FastAPI backend — routers, services, repositories, schemas, database models, config, or auth. It defines the layered architecture, folder structure, RBAC enforcement pattern, and forward-compatibility hooks required so the planned text-to-SQL conversational layer can be added later without refactoring. Apply this before creating or editing any backend file, not just when explicitly asked about "architecture."
---

# MONGA Backend Architecture & System Design

## 1. Project context

MONGA is a sales forecasting and analytics platform for a multi-location Taiwanese
street food business in the Philippines. Stack: **FastAPI** (backend), **Next.js/TypeScript**
(frontend), **PostgreSQL** (warehouse), **LightGBM/XGBoost** (forecasting).

Four business objectives drive the domain model — every router/service module should
map to one of these, not to a generic CRUD resource:

1. **Demand planning** — hourly/daily/weekly transaction forecasts (staffing, poultry & oil procurement)
2. **Menu mix optimization** — margin vs. volume analysis, pricing simulation
3. **Wastage mitigation** — perishable-ingredient forecasting
4. **Multi-location comparison** — mall anchors vs. neighborhood/grocery locations

An RBAC schema already exists (`monga_user_schema.sql`): UUID users, a `user_roles`
join table, and a `user_stores` scoping table (`VARCHAR(10)` FKs to `stores`). Roles:
`admin`, `regional_manager`, `branch_manager`, `analyst`, `staff`.

**A conversational text-to-SQL layer is planned but not yet built.** It will let users
ask natural-language questions that get turned into SQL and answered with a chart.
Everything in this document is written so that feature slots in later without
reshaping the rest of the backend. Treat "will this make the chatbot harder to add?"
as a standing design constraint, not a someday-concern.

---

## 2. Core architectural principles

**Strict layering, one direction of dependency:**

```
router  →  service  →  repository  →  db session
 (HTTP)     (business     (data access,
             logic)        SQL/ORM only)
```

- **Routers** parse/validate the request (via Pydantic), call exactly one service
  method, and shape the HTTP response. No business logic, no SQL, no direct DB session use.
- **Services** own business logic and orchestration (e.g., "get forecast" may call
  the repository, then the ML inference module, then combine results). Services
  never touch `Request`/`Response` objects — they're framework-agnostic and unit-testable.
- **Repositories** are the only layer allowed to write SQL/ORM queries. They accept
  a scoping context (see §5) and return domain objects, never raw rows to the router.
- **Core** holds cross-cutting concerns: config, DB engine/session factory, security/auth
  dependencies, logging.

Why this matters specifically for MONGA: the future chatbot's guardrail-and-execute
layer needs to reuse the *same* RBAC scoping and the *same* read-only connection pool
that the rest of the app uses. If SQL is scattered across routers today, there's no
single place to reuse later — it has to live in the repository layer from day one.

**Other standing rules:**
- Pydantic schemas at every API boundary. Never return an ORM model or a raw dict
  from a router.
- Single Responsibility per module: one router file, one service file, one repository
  file per business domain (`forecasting`, `menu`, `wastage`, `locations`), not one
  giant `crud.py`.
- Dependency inversion for anything that will later be swapped or mocked (DB session,
  current-user/role resolution) — inject via FastAPI's `Depends()`, don't import globals.

---

## 3. Folder structure (standard for `backend/`)

```
backend/
├── main.py                    # app factory, router registration, middleware, CORS
├── core/
│   ├── config.py               # pydantic-settings BaseSettings, reads .env
│   ├── db.py                   # engine(s) + session factory; see §5 for dual-pool setup
│   ├── security.py             # JWT, password hashing, get_current_user dependency
│   └── logging.py
├── routers/                    # thin HTTP layer, one file per domain
│   ├── auth.py
│   ├── forecasting.py
│   ├── menu.py
│   ├── wastage.py
│   ├── locations.py
│   └── chat.py                 # placeholder now — see §7
├── services/                   # business logic, framework-agnostic
│   ├── forecasting_service.py
│   ├── menu_service.py
│   ├── wastage_service.py
│   ├── location_service.py
│   └── chat_service.py         # placeholder now — see §7
├── repositories/                # the ONLY layer that writes SQL/ORM queries
│   ├── base.py                  # shared scoping helpers (store-filter, role-filter)
│   ├── sales_repository.py
│   ├── inventory_repository.py
│   └── location_repository.py
├── models/                      # SQLAlchemy ORM models mirroring the warehouse
├── schemas/                     # Pydantic request/response models
│   ├── forecasting.py
│   ├── menu.py
│   ├── auth.py
│   └── chat.py
├── ml/
│   ├── training/
│   ├── inference/
│   └── registry.py              # model versioning/loading
├── guardrails/                  # placeholder now — text-to-SQL allow-list & validator
└── tests/
    ├── unit/                    # services with mocked repositories
    └── integration/             # RBAC scoping tests — see §5
```

Populate `backend/` in this order: `core/config.py` → `core/db.py` → `core/security.py`
→ one full vertical slice (router → service → repository → schema) for a single
endpoint → repeat per domain. Don't build all routers before any repository exists.

---

## 4. API design conventions

- Prefix all routes with `/api/v1/...`. Versioning from day one avoids breaking the
  frontend when the schema evolves.
- Resource-oriented paths (`/api/v1/forecasts/daily`, not `/api/v1/getDailyForecast`).
- Every endpoint has an explicit `response_model=`. Never rely on FastAPI's implicit
  serialization of an ORM object.
- Consistent error shape across the app (e.g. `{"detail": str, "code": str}`), raised
  via a shared `HTTPException` helper in `core/`, not inline `raise HTTPException(...)`
  scattered per router with inconsistent payloads.
- List endpoints are paginated (`limit`/`offset` or cursor) from the start —
  multi-location data grows fast and an unpaginated `/locations/{id}/transactions`
  becomes a problem quickly.
- Use `async def` for endpoints and repository calls once the DB driver is async
  (`asyncpg`/SQLAlchemy async). Forecasting and future LLM calls are both I/O-bound;
  sync endpoints will bottleneck under load.

---

## 5. Database access & RBAC — the part that must be right

**Two connection pools from the start, not one:**

```python
# core/db.py (illustrative shape, not full implementation)
app_engine = create_async_engine(settings.APP_DATABASE_URL)       # read-write, app role
analytics_engine = create_async_engine(settings.ANALYTICS_DATABASE_URL)  # read-only role
```

The app pool is for normal CRUD (auth, orders, inventory writes). The read-only
analytics pool is for anything that only reads and aggregates — forecasting queries,
dashboard endpoints, and later the chatbot's guardrail-and-execute layer. Standing up
this split now, and routing forecasting/analytics repositories through it, means the
chatbot doesn't require a database or credentials change later — it just becomes
another consumer of the existing read-only pool.

**RBAC scoping happens in the repository layer, not just the router:**

```python
# core/security.py (illustrative)
async def get_current_scope(token: str = Depends(oauth2_scheme)) -> UserScope:
    """Resolves user_roles + user_stores into a UserScope(role, store_ids)."""
    ...

# repositories/base.py (illustrative)
def apply_store_scope(query, scope: UserScope):
    """Every repository method that touches store-level data calls this."""
    if scope.role == "admin":
        return query
    return query.where(SalesFact.store_id.in_(scope.store_ids))
```

Pass `UserScope` (or a `role` + `store_ids` context) into every repository call.
This is the single most important pattern in the backend: a `branch_manager` for
WalterMart must be structurally unable to query SM Mall of Asia's data, whether the
request comes from a normal dashboard endpoint or, later, from an LLM-generated SQL
query. If scoping is enforced only in routers, the guardrail layer will have to
reimplement it from scratch and can drift out of sync. Enforce it once, in the
repository/query-building layer, and everything built on top inherits it.

- Never string-concatenate user input into SQL. Use parameterized queries/ORM
  constructs everywhere, including in any future guardrail-generated SQL.
- Add integration tests specifically for cross-store leakage (§9) — this is the
  category of bug that's invisible until it's a real incident.

---

## 6. Config, environments, CORS

- `core/config.py` uses `pydantic-settings.BaseSettings`, loading from `.env`
  (never commit secrets; `.env` stays gitignored, `.env.example` documents required vars).
- Required settings to define now even if unused yet: `APP_DATABASE_URL`,
  `ANALYTICS_DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`, and placeholders for
  `LLM_API_KEY` / `LLM_MODEL` (unset in dev, used once the chatbot ships).
- CORS: since Next.js (`monga-web-app/`) and FastAPI run on different ports in dev,
  configure `CORSMiddleware` in `main.py` with `CORS_ORIGINS` from settings (e.g.
  `http://localhost:3000`), not a wildcard, even in dev.

---

## 7. Forward compatibility: designing now for the chatbot later

The text-to-SQL conversational layer is: **prompt builder (schema + few-shot examples)
→ LLM SQL generation → guardrail-and-execute (read-only role, allow-listed tables,
RBAC scoping) → LLM summarization/chart suggestion.** To make that a clean addition
rather than a rewrite:

- **Reserve the module now.** `routers/chat.py`, `services/chat_service.py`,
  `schemas/chat.py`, and `guardrails/` can exist as near-empty stubs today. This keeps
  the folder convention consistent and means the eventual implementation is additive.
- **Build one semantic layer, used by both dashboards and chat.** Define canonical
  metric names, units, and allowed groupings (e.g. "daily net sales", "wastage rate
  by ingredient") in one place (`core/` or a `semantics/` module). Dashboard endpoints
  and the future LLM prompt builder should both read from this, so a metric never
  means two different things depending on which surface computed it.
- **Route analytics/forecasting repositories through the read-only pool now** (§5),
  so the guardrail-execute layer is just another caller of infrastructure that already
  exists and is already scoped correctly.
- **Plan a `conversations` / `messages` table pair** in the same warehouse, scoped by
  `user_id`/`store_ids` like everything else — don't special-case chat data outside
  the RBAC model.
- **Log every generated SQL statement** (query text, user, role, store scope, timestamp)
  once the guardrail layer exists — this is a compliance/audit surface, not optional
  logging. Put the hook point in `guardrails/` now so it's obvious where this goes.
- **Expect a caching layer** (e.g. Redis) for repeated question→SQL patterns, given
  two LLM calls per query (generation + summarization) is costly in both latency and
  spend. Don't design the chat service to assume every request hits the LLM.

---

## 8. Testing & observability

- **Unit tests** for services, with repositories mocked — test business logic in
  isolation from the database.
- **Integration tests** for RBAC scoping specifically: for each role, assert that
  queries return only permitted stores' data. This is the highest-value test suite
  in the codebase given the multi-location, multi-role model.
- Structured logging with request IDs; log at the service layer (decisions), not
  just the router layer (HTTP in/out).
- Once the chatbot exists, add a test category for guardrail rejection: malformed or
  out-of-scope generated SQL must fail closed, not silently execute a subset.

---

## 9. Anti-patterns to avoid

- Calling the database directly from a router, "just this once."
- `SELECT *` anywhere — always explicit columns, so schema changes don't silently
  leak new columns into API responses or (later) into LLM-visible query results.
- Re-implementing role/store checks inline per-endpoint instead of using the shared
  `UserScope` + `apply_store_scope` pattern.
- Giving any future LLM-facing database credential write access, ever — the guardrail
  layer's DB role must be read-only at the Postgres level, not just "read-only by
  convention" in application code.
- Building the chatbot's SQL generation against the app's write-capable connection
  "temporarily" to save setup time — the two-pool split in §5 exists precisely to
  prevent this shortcut from becoming permanent.
