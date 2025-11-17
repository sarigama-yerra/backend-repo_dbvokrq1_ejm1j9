import os
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from uuid import uuid4

from database import db, create_document, get_documents
from schemas import Fleetvehicle, Claim, Testimonial, Post, Contactmessage

app = FastAPI(title="Prestige Car Hire Management LTD API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"name": "Prestige Car Hire Management LTD", "status": "ok"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', "Unknown")
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# -------------------- Fleet Endpoints --------------------
@app.get("/api/fleet")
async def list_fleet(q: Optional[str] = None, type: Optional[str] = None, fuel: Optional[str] = None, transmission: Optional[str] = None, seats: Optional[int] = None):
    filters = {}
    if q:
        # simple contains search across make/model
        filters["$or"] = [
            {"make": {"$regex": q, "$options": "i"}},
            {"model": {"$regex": q, "$options": "i"}}
        ]
    if type:
        filters["type"] = {"$regex": f"^{type}$", "$options": "i"}
    if fuel:
        filters["fuel"] = {"$regex": f"^{fuel}$", "$options": "i"}
    if transmission:
        filters["transmission"] = {"$regex": f"^{transmission}$", "$options": "i"}
    if seats:
        filters["seats"] = seats

    docs = get_documents("fleetvehicle", filters)
    # normalize _id to string
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

@app.post("/api/fleet")
async def create_fleet_item(item: Fleetvehicle):
    new_id = create_document("fleetvehicle", item)
    return {"id": new_id}

# -------------------- Testimonials --------------------
@app.get("/api/testimonials")
async def get_testimonials(limit: int = 10):
    docs = get_documents("testimonial", {}, limit)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

@app.post("/api/testimonials")
async def create_testimonial(item: Testimonial):
    new_id = create_document("testimonial", item)
    return {"id": new_id}

# -------------------- Blog/News --------------------
@app.get("/api/posts")
async def get_posts():
    docs = get_documents("post", {"published": True})
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

@app.post("/api/posts")
async def create_post(item: Post):
    new_id = create_document("post", item)
    return {"id": new_id}

# -------------------- Contact --------------------
@app.post("/api/contact")
async def submit_contact(msg: Contactmessage):
    new_id = create_document("contactmessage", msg)
    return {"id": new_id}

# -------------------- Claims with File Upload --------------------
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/claim")
async def submit_claim(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    incident_date: str = Form(...),
    incident_location: str = Form(...),
    description: str = Form(...),
    policy_number: Optional[str] = Form(None),
    vehicle_reg: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    stored_paths: List[str] = []
    if files:
        for f in files:
            ext = os.path.splitext(f.filename)[1]
            fname = f"{uuid4().hex}{ext}"
            dest = os.path.join(UPLOAD_DIR, fname)
            with open(dest, "wb") as out:
                out.write(await f.read())
            stored_paths.append(dest)

    data = Claim(
        full_name=full_name,
        email=email,
        phone=phone,
        incident_date=incident_date,
        incident_location=incident_location,
        description=description,
        policy_number=policy_number,
        vehicle_reg=vehicle_reg,
        files=stored_paths
    )
    new_id = create_document("claim", data)
    return {"id": new_id, "files": stored_paths}

# --------------- Schema Introspection (for viewer) ---------------
class SchemaResponse(BaseModel):
    models: List[str]

@app.get("/schema", response_model=SchemaResponse)
async def schema_endpoint():
    return SchemaResponse(models=[
        "Fleetvehicle", "Claim", "Testimonial", "Post", "Contactmessage"
    ])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
