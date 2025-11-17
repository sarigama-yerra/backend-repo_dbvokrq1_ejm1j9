"""
Database Schemas for Prestige Car Hire Management LTD

Each Pydantic model represents a MongoDB collection. The collection name is the lowercase of the class name.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class Fleetvehicle(BaseModel):
    make: str = Field(...)
    model: str = Field(...)
    year: int = Field(..., ge=1990, le=2100)
    type: str = Field(..., description="e.g., Saloon, Estate, SUV, Coupe")
    transmission: str = Field(..., description="Automatic or Manual")
    fuel: str = Field(..., description="Petrol, Diesel, Hybrid, Electric")
    seats: int = Field(..., ge=2, le=9)
    daily_rate: float = Field(..., ge=0)
    colour: Optional[str] = None
    image: Optional[str] = Field(None, description="URL of vehicle image")
    tags: Optional[List[str]] = None

class Claim(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    incident_date: str
    incident_location: str
    description: str
    policy_number: Optional[str] = None
    vehicle_reg: Optional[str] = None
    files: Optional[List[str]] = Field(default=None, description="Stored file paths")

class Testimonial(BaseModel):
    name: str
    role: Optional[str] = None
    content: str
    rating: Optional[int] = Field(default=5, ge=1, le=5)

class Post(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    image: Optional[str] = None
    published: bool = True

class Contactmessage(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str
