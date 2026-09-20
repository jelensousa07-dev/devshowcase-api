from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DevShowcase API - Juana Elen de Sousa e Silva e Edinael de Carvalho Nunes",
    description="Atividade 1 para a disciplina de Programação Backend - Curso de Tecnologia em Sistemas para Internet.",
    version="1.0"
)

@app.get("/")
def testar_api():
    return {"mensagem": "A minha API está viva e a funcionar!"}

# --- PERFIS ---
@app.post("/profiles/", response_model=schemas.ProfileResponse)
def create_profile(profile: schemas.ProfileCreate, db: Session = Depends(get_db)):
    db_profile = models.ProfileModel(name=profile.name, bio=profile.bio, github_url=profile.github_url)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@app.get("/profiles/", response_model=list[schemas.ProfileResponse])
def list_profiles(db: Session = Depends(get_db)):
    return db.query(models.ProfileModel).all()


# --- TECNOLOGIAS ---
@app.post("/technologies/", response_model=schemas.TechnologyResponse)
def create_technology(tech: schemas.TechnologyCreate, db: Session = Depends(get_db)):
    db_tech = db.query(models.TechnologyModel).filter(models.TechnologyModel.name == tech.name).first()
    if db_tech:
        return db_tech  # Retorna se já existir
    db_tech = models.TechnologyModel(name=tech.name)
    db.add(db_tech)
    db.commit()
    db.refresh(db_tech)
    return db_tech

@app.get("/technologies/", response_model=list[schemas.TechnologyResponse])
def list_technologies(db: Session = Depends(get_db)):
    return db.query(models.TechnologyModel).all()


# --- PROJETOS ---
@app.post("/projects/", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_profile = db.query(models.ProfileModel).filter(models.ProfileModel.id == project.profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")

    db_project = models.ProjectModel(
        title=project.title,
        description=project.description,
        project_url=project.project_url,
        profile_id=project.profile_id
    )
    
    # Adicionar tecnologias associadas, se houver
    if project.technology_ids:
        techs = db.query(models.TechnologyModel).filter(models.TechnologyModel.id.in_(project.technology_ids)).all()
        db_project.technologies = techs

    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/", response_model=list[schemas.ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.ProjectModel).all()


# --- FEEDBACKS ---
@app.post("/feedbacks/", response_model=schemas.FeedbackResponse)
def create_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    db_project = db.query(models.ProjectModel).filter(models.ProjectModel.id == feedback.project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    db_feedback = models.FeedbackModel(
        comment=feedback.comment,
        author=feedback.author,
        project_id=feedback.project_id
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@app.get("/feedbacks/", response_model=list[schemas.FeedbackResponse])
def list_feedbacks(db: Session = Depends(get_db)):
    return db.query(models.FeedbackModel).all()