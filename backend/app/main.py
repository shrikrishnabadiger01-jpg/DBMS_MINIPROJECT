from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import test_connection
from pydantic import BaseModel, Field
from typing import Optional, Literal
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


class CaseCreate(BaseModel):
    FIRNumber: str = Field(min_length=1, max_length=30)
    CrimeID: int
    OfficerID: int
    CaseStatus: Literal["Open", "Under Investigation", "Closed"] = "Open"
    OpenedDate: Optional[date] = None


class CaseUpdate(BaseModel):
    FIRNumber: Optional[str] = Field(default=None, min_length=1, max_length=30)
    CrimeID: Optional[int] = None
    OfficerID: Optional[int] = None
    CaseStatus: Optional[Literal["Open", "Under Investigation", "Closed"]] = None
    ClosedDate: Optional[date] = None


@app.get("/cases/{case_id}")
def get_case_details(case_id: int):
    case_query = text("""
        SELECT
            cd.CaseID,
            cd.FIRNumber,
            cd.CrimeID,
            cr.CrimeType,
            cd.OfficerID,
            po.OfficerName,
            cd.CaseStatus,
            cd.OpenedDate,
            cd.ClosedDate
        FROM CaseDetails cd
        JOIN Crime cr
            ON cd.CrimeID = cr.CrimeID
        JOIN PoliceOfficer po
            ON cd.OfficerID = po.OfficerID
        WHERE cd.CaseID = :case_id
    """)

    linked_query = text("""
        SELECT
            cc.CriminalID,
            c.FullName,
            cc.PersonRole
        FROM CriminalCase cc
        JOIN Criminal c
            ON cc.CriminalID = c.CriminalID
        WHERE cc.CaseID = :case_id
        ORDER BY c.FullName
    """)

    with engine.connect() as connection:
        case_row = connection.execute(case_query, {"case_id": case_id}).first()
        if case_row is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Case not found")

        linked = [dict(row._mapping) for row in connection.execute(linked_query, {"case_id": case_id})]

    return {
        "case": dict(case_row._mapping),
        "criminals": linked,
    }


@app.post("/cases", status_code=201)
def create_case(case: CaseCreate):
    opened_date = case.OpenedDate or date.today()
    query = text("""
        INSERT INTO CaseDetails (FIRNumber, CrimeID, OfficerID, CaseStatus, OpenedDate, ClosedDate)
        VALUES (:fir_number, :crime_id, :officer_id, :case_status, :opened_date, :closed_date)
    """)

    with engine.begin() as connection:
        result = connection.execute(query, {
            "fir_number": case.FIRNumber.strip(),
            "crime_id": case.CrimeID,
            "officer_id": case.OfficerID,
            "case_status": case.CaseStatus,
            "opened_date": opened_date,
            "closed_date": None if case.CaseStatus != "Closed" else opened_date,
        })
        case_id = result.lastrowid

    return {
        "message": "Case record created",
        "CaseID": case_id,
    }


@app.put("/cases/{case_id}")
def update_case(case_id: int, case: CaseUpdate):
    existing_query = text("SELECT CaseID, FIRNumber, CrimeID, OfficerID, CaseStatus, ClosedDate FROM CaseDetails WHERE CaseID = :case_id")
    update_fields = []
    values = {"case_id": case_id}

    with engine.begin() as connection:
        existing = connection.execute(existing_query, {"case_id": case_id}).first()
        if existing is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Case not found")

        payload = case.model_dump(exclude_unset=True)
        if "FIRNumber" in payload and payload["FIRNumber"] is not None:
            update_fields.append("FIRNumber = :fir_number")
            values["fir_number"] = payload["FIRNumber"].strip()
        if "CrimeID" in payload and payload["CrimeID"] is not None:
            update_fields.append("CrimeID = :crime_id")
            values["crime_id"] = payload["CrimeID"]
        if "OfficerID" in payload and payload["OfficerID"] is not None:
            update_fields.append("OfficerID = :officer_id")
            values["officer_id"] = payload["OfficerID"]
        if "CaseStatus" in payload and payload["CaseStatus"] is not None:
            new_status = payload["CaseStatus"]
            update_fields.append("CaseStatus = :case_status")
            values["case_status"] = new_status
            if new_status == "Closed":
                update_fields.append("ClosedDate = :closed_date")
                values["closed_date"] = payload.get("ClosedDate") or date.today()
            else:
                update_fields.append("ClosedDate = NULL")
        if "ClosedDate" in payload and payload["ClosedDate"] is not None:
            update_fields.append("ClosedDate = :closed_date")
            values["closed_date"] = payload["ClosedDate"]

        if not update_fields:
            return {"message": "No case changes provided"}

        query = text(f"UPDATE CaseDetails SET {', '.join(update_fields)} WHERE CaseID = :case_id")
        connection.execute(query, values)

    return {"message": "Case updated successfully", "CaseID": case_id}


@app.get("/crimes")
def get_crimes():
    query = text("""
        SELECT CrimeID, CrimeType
        FROM Crime
        ORDER BY CrimeType
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        crimes = [dict(row._mapping) for row in result]

    return {"crimes": crimes}


@app.get("/officers")
def get_officers():
    query = text("""
        SELECT OfficerID, OfficerName, RankName, StationID
        FROM PoliceOfficer
        ORDER BY OfficerName
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        officers = [dict(row._mapping) for row in result]

    return {"officers": officers}


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


@app.delete("/criminal-cases/{criminal_id}/{case_id}")
def unlink_criminal_from_case(criminal_id: int, case_id: int):
    query = text("""
        DELETE FROM CriminalCase
        WHERE CriminalID = :criminal_id AND CaseID = :case_id
    """)

    with engine.begin() as connection:
        result = connection.execute(query, {"criminal_id": criminal_id, "case_id": case_id})

    if result.rowcount == 0:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Link not found")

    return {"message": "Criminal unlinked from case successfully"}
