from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Tabela de associação para a relação N para N entre Project e Technology
project_technology = Table(
    "project_technology",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("technology_id", Integer, ForeignKey("technologies.id"), primary_key=True)
)

class ProfileModel(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    github_url = Column(String, nullable=False)

    # Relacionamento: Um perfil pode ter vários projetos (1 para N)
    projects = relationship("ProjectModel", back_populates="owner", cascade="all, delete-orphan")

class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    project_url = Column(String, nullable=True)
    upvotes = Column(Integer, default=0)
average_rating = Column(Float, default=0.0) 
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)

    # Relacionamentos
    owner = relationship("ProfileModel", back_populates="projects")
    technologies = relationship("TechnologyModel", secondary=project_technology, back_populates="projects")
    feedbacks = relationship("FeedbackModel", back_populates="project", cascade="all, delete-orphan")

class TechnologyModel(Base):
    __tablename__ = "technologies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    projects = relationship("ProjectModel", secondary=project_technology, back_populates="technologies")

class FeedbackModel(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(Text, nullable=False)
    author = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    project = relationship("ProjectModel", back_populates="feedbacks")