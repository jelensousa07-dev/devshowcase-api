from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table
from sqlalchemy.orm import relationship
from database import Base

project_technology = Table(
    "project_technology",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("technology_id", Integer, ForeignKey("technologies.id"), primary_key=True),
)

class ProfileModel(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    bio = Column(String)
    github_url = Column(String)

    projects = relationship("ProjectModel", back_populates="owner")

class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    upvotes = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    owner = relationship("ProfileModel", back_populates="projects")
    
    feedbacks = relationship("FeedbackModel", back_populates="project", cascade="all, delete-orphan")
    technologies = relationship("TechnologyModel", secondary=project_technology, back_populates="projects")

class FeedbackModel(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String)
    author = Column(String)
    rating = Column(Integer)
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("ProjectModel", back_populates="feedbacks")

class TechnologyModel(Base):
    __tablename__ = "technologies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    projects = relationship("ProjectModel", secondary=project_technology, back_populates="technologies")