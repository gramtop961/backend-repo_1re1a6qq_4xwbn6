import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import create_document, get_documents, db
from schemas import Appointment

app = FastAPI(title="Jambi Skin Centre API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Jambi Skin Centre Backend is running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from Jambi Skin Centre API"}


@app.get("/api/services")
def list_services() -> List[dict]:
    services = [
        {
            "id": "facial-signature",
            "name": "Signature Facial",
            "description": "Perawatan dasar untuk membersihkan, exfoliasi, dan hidrasi kulit.",
            "price": 250000,
            "duration": 60,
        },
        {
            "id": "acne-peel",
            "name": "Acne Peel",
            "description": "Chemical peeling ringan untuk kulit berjerawat dan berkomedo.",
            "price": 350000,
            "duration": 45,
        },
        {
            "id": "laser-bright",
            "name": "Laser Brightening",
            "description": "Toning laser untuk meratakan warna kulit dan mencerahkan.",
            "price": 900000,
            "duration": 30,
        },
        {
            "id": "botox",
            "name": "Botox",
            "description": "Perawatan untuk mengurangi kerutan halus pada wajah.",
            "price": 2500000,
            "duration": 30,
        },
    ]
    return services


class AppointmentRequest(BaseModel):
    name: str
    phone: str
    service: str
    preferred_date: str
    note: Optional[str] = None


@app.post("/api/appointments")
def create_appointment(payload: AppointmentRequest):
    try:
        # Validate using schema then insert
        appt = Appointment(**payload.model_dump())
        inserted_id = create_document("appointment", appt)
        return {"status": "success", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/appointments")
def recent_appointments(limit: int = 10):
    try:
        docs = get_documents("appointment", limit=limit)
        # Convert ObjectId to string for response
        sanitized = []
        for d in docs:
            d["_id"] = str(d.get("_id"))
            sanitized.append(d)
        return {"items": sanitized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/info")
def clinic_info():
    return {
        "name": "Jambi Skin Centre",
        "tagline": "Perawatan kulit tepercaya di Jambi",
        "address": "Jl. Contoh No. 123, Jambi",
        "phone": "+62 811-1234-567",
        "whatsapp": "+62 811-1234-567",
        "hours": {
            "mon_fri": "09.00 - 19.00",
            "sat": "09.00 - 17.00",
            "sun": "Tutup",
        },
        "socials": {
            "instagram": "https://instagram.com/jambiskincentre",
            "tiktok": "https://tiktok.com/@jambiskincentre",
        },
    }


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
