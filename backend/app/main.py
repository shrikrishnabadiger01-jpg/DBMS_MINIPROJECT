from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import test_connection
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from sqlalchemy import text
from app.database import engine

app = FastAPI(title="Criminal Database Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "CDBMS backend is running!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/db-test")
def db_test():
    try:
        return {
            "status": "connected",
            "database": test_connection()
        }
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail="Database connection failed. Check backend configuration."
        )

    
from sqlalchemy import text
from app.database import engine

@app.get("/cases")
def get_cases():
    query = text("""
        SELECT
            cd.CaseID,
            cd.FIRNumber,
            cr.CrimeType,
            po.OfficerName,
            cd.CaseStatus,
            cd.OpenedDate
        FROM CaseDetails cd
        JOIN Crime cr
            ON cd.CrimeID = cr.CrimeID
        JOIN PoliceOfficer po
            ON cd.OfficerID = po.OfficerID
        ORDER BY cd.CaseID
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        cases = [dict(row._mapping) for row in result]

    return {"cases": cases}

class CriminalCreate(BaseModel):
    FullName: str = Field(min_length=1, max_length=100)
    DateOfBirth: Optional[date] = None
    Address: Optional[str] = Field(default=None, max_length=200)


@app.get("/criminals")
def get_criminals():
    query = text("""
        SELECT CriminalID, FullName, DateOfBirth, Address
        FROM Criminal
        ORDER BY CriminalID
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        criminals = [dict(row._mapping) for row in result]

    return {"criminals": criminals}


@app.post("/criminals", status_code=201)
def create_criminal(criminal: CriminalCreate):
    query = text("""
        INSERT INTO Criminal (FullName, DateOfBirth, Address)
        VALUES (:name, :dob, :address)
    """)

    with engine.begin() as connection:
        result = connection.execute(query, {
            "name": criminal.FullName.strip(),
            "dob": criminal.DateOfBirth,
            "address": criminal.Address
        })

        criminal_id = result.lastrowid

    return {
        "message": "Criminal record created",
        "CriminalID": criminal_id
    }


@app.get("/criminals/{criminal_id}/cases")
def get_criminal_cases(criminal_id: int):
    query = text("""
        SELECT
            c.CriminalID,
            c.FullName,
            cd.CaseID,
            cd.FIRNumber,
            cr.CrimeType,
            cc.PersonRole,
            cd.CaseStatus,
            cd.OpenedDate
        FROM CriminalCase cc
        JOIN Criminal c
            ON cc.CriminalID = c.CriminalID
        JOIN CaseDetails cd
            ON cc.CaseID = cd.CaseID
        JOIN Crime cr
            ON cd.CrimeID = cr.CrimeID
        WHERE c.CriminalID = :criminal_id
        ORDER BY cd.CaseID
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query, {"criminal_id": criminal_id}
        )
        records = [dict(row._mapping) for row in result]

    return {"criminal_id": criminal_id, "cases": records}


from pydantic import BaseModel
from typing import Literal

class CriminalCaseCreate(BaseModel):
    CriminalID: int
    CaseID: int
    PersonRole: Literal["Suspect", "Accused", "Witness", "Convicted"]


@app.post("/criminal-cases", status_code=201)
def link_criminal_to_case(link: CriminalCaseCreate):
    query = text("""
        INSERT INTO CriminalCase (CriminalID, CaseID, PersonRole)
        VALUES (:criminal_id, :case_id, :role)
    """)

    try:
        with engine.begin() as connection:
            connection.execute(
                query,
                {
                    "criminal_id": link.CriminalID,
                    "case_id": link.CaseID,
                    "role": link.PersonRole,
                },
            )

        return {"message": "Criminal linked to case successfully"}

    except Exception as exc:
        from sqlalchemy.exc import IntegrityError

        if isinstance(exc, IntegrityError):
            from fastapi import HTTPException

            raise HTTPException(
                status_code=409,
                detail=(
                    "Could not link this criminal to the case. "
                    "Check that both IDs exist and that the link "
                    "does not already exist."
                ),
            )

        raise
