# Criminal Database Management System — System Architecture

This diagram describes the current implementation and local development configuration.

```mermaid
flowchart TB
    user["User"]

    subgraph presentation["Presentation tier — Browser / React + Vite · localhost:5173"]
        ui["App.jsx<br/>Dashboard and record tables<br/>Case creation and status updates<br/>Criminal creation and case linking / unlinking<br/>Client-side search and filtering"]
        client["api.js<br/>Fetch API client<br/>JSON requests and response / error handling"]
        ui <-->|"Function calls / results"| client
    end

    subgraph application["Application tier — Python / FastAPI · localhost:8000"]
        api["main.py — REST endpoints<br/>CORS: allows http://localhost:5173<br/>Pydantic request validation"]
        logic["Route handlers in main.py<br/>Case, criminal and relationship operations<br/>Case status / closed-date rules<br/>Parameterized SQL queries"]
        access["database.py<br/>SQLAlchemy engine + PyMySQL<br/>Connection pool with pre-ping<br/>Read connections / write transactions"]
        api --> logic --> access
    end

    subgraph persistence["Data tier — MySQL · default localhost:3306"]
        db[("CriminalDB<br/>CaseDetails · Crime · PoliceOfficer<br/>Criminal · CriminalCase")]
    end

    config["Environment variables / .env<br/>DB_HOST · DB_PORT · DB_USER<br/>DB_PASSWORD · DB_NAME"]
    user <-->|"View records / submit forms"| ui
    client <-->|"HTTP REST / JSON<br/>GET · POST · PUT · DELETE"| api
    access <-->|"SQL / rows<br/>Commit or rollback writes"| db
    config -.->|"Connection settings"| access

    classDef frontend fill:#e8f1ff,stroke:#2563eb,color:#172554;
    classDef backend fill:#ecfdf5,stroke:#059669,color:#064e3b;
    classDef storage fill:#fff7ed,stroke:#ea580c,color:#7c2d12;
    class ui,client frontend;
    class api,logic,access backend;
    class db storage;
```

## API responsibilities

| Feature | Endpoints |
| --- | --- |
| Cases | `GET /cases`, `POST /cases`, `GET /cases/{case_id}`, `PUT /cases/{case_id}` |
| Criminal records | `GET /criminals`, `POST /criminals`, `GET /criminals/{criminal_id}/cases` |
| Case associations | `POST /criminal-cases`, `DELETE /criminal-cases/{criminal_id}/{case_id}` |
| Reference data | `GET /crimes`, `GET /officers` |
| Service checks | `GET /`, `GET /health`, `GET /db-test` |

## Request flow

1. The React application loads cases, criminals, crimes and officers through `api.js`. Search, status filters and dashboard counts run in the browser.
2. User form submissions send JSON to FastAPI, which validates request bodies with Pydantic and executes the corresponding route handler.
3. Handlers execute parameterized SQL through the SQLAlchemy engine and PyMySQL driver. Writes use `engine.begin()` transactions; reads use `engine.connect()`.
4. FastAPI returns JSON records, success messages or errors. React updates its state and refreshes records after successful changes.

## Implementation boundaries

- API routes, validation models and business rules currently reside together in `backend/app/main.py`; the diagram separates their responsibilities logically.
- Database configuration and the shared engine reside in `backend/app/database.py`. Queries use SQLAlchemy SQL expressions rather than ORM models; the declared `SessionLocal` is not used by the current handlers.
- The tables shown are referenced by backend SQL. Schema creation scripts are not present in this repository, so this is not a verified database schema diagram.
- The backend also exposes case-detail and criminal-case-history reads that currently have no wrappers in `frontend/src/api.js`.
- `/health` reports service health without querying MySQL; `/db-test` checks database connectivity.
- No authentication layer or production deployment configuration is implemented in the inspected source.

## Source files

- [React UI](../frontend/src/App.jsx)
- [HTTP client](../frontend/src/api.js)
- [FastAPI routes and validation](../backend/app/main.py)
- [Database connection](../backend/app/database.py)
- [Vite configuration](../frontend/vite.config.js)
