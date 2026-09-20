from pydantic import BaseModel
from typing import Optional, List

# --- SCHEMAS PARA PROFILE ---
class ProfileBase(BaseModel):
    name: str
    bio: Optional[str] = None
    github_url: str

class ProfileCreate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: int

    class Config:
        from_attributes = True


# --- SCHEMAS PARA TECHNOLOGY ---
class TechnologyBase(BaseModel):
    name: str

class TechnologyCreate(TechnologyBase):
    pass

class TechnologyResponse(TechnologyBase):
    id: int

    class Config:
        from_attributes = True


# --- SCHEMAS PARA PROJECT ---
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_url: Optional[str] = None

class ProjectCreate(ProjectBase):
    profile_id: int
    technology_ids: List[int] = []

class ProjectResponse(ProjectBase):
    id: int
    profile_id: int
    technologies: List[TechnologyResponse] = []

    class Config:
        from_attributes = True


# --- SCHEMAS PARA FEEDBACK ---
class FeedbackBase(BaseModel):
    comment: str
    author: str

class FeedbackCreate(FeedbackBase):
    project_id: int

class FeedbackResponse(FeedbackBase):
    id: int
    project_id: int

    class Config:
        from_attributes = True