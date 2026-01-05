"""JSON Resume schema models using Pydantic."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, EmailStr


class Location(BaseModel):
    address: Optional[str] = None
    postalCode: Optional[str] = None
    city: Optional[str] = None
    countryCode: Optional[str] = None
    region: Optional[str] = None


class Profile(BaseModel):
    network: Optional[str] = None
    username: Optional[str] = None
    url: Optional[str] = None


class Basics(BaseModel):
    name: Optional[str] = None
    label: Optional[str] = None
    image: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[Location] = None
    profiles: list[Profile] = Field(default_factory=list)


class Work(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    url: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    summary: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)


class Volunteer(BaseModel):
    organization: Optional[str] = None
    position: Optional[str] = None
    url: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    summary: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)


class Education(BaseModel):
    institution: Optional[str] = None
    url: Optional[str] = None
    area: Optional[str] = None
    studyType: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    score: Optional[str] = None
    courses: list[str] = Field(default_factory=list)


class Award(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    awarder: Optional[str] = None
    summary: Optional[str] = None


class Certificate(BaseModel):
    name: Optional[str] = None
    date: Optional[str] = None
    issuer: Optional[str] = None
    url: Optional[str] = None


class Publication(BaseModel):
    name: Optional[str] = None
    publisher: Optional[str] = None
    releaseDate: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None


class Skill(BaseModel):
    name: Optional[str] = None
    level: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)


class Language(BaseModel):
    language: Optional[str] = None
    fluency: Optional[str] = None


class Interest(BaseModel):
    name: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)


class Reference(BaseModel):
    name: Optional[str] = None
    reference: Optional[str] = None


class Project(BaseModel):
    name: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    description: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)
    url: Optional[str] = None


class Resume(BaseModel):
    """Complete JSON Resume schema model."""
    
    basics: Optional[Basics] = None
    work: list[Work] = Field(default_factory=list)
    volunteer: list[Volunteer] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    awards: list[Award] = Field(default_factory=list)
    certificates: list[Certificate] = Field(default_factory=list)
    publications: list[Publication] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)
    interests: list[Interest] = Field(default_factory=list)
    references: list[Reference] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
