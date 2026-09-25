from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DevShowcase API - Juana Elen de Sousa e Silva e Edinael de Carvalho Nunes",
    description="Atividade 2 para a disciplina de Programação Backend - Curso de Tecnologia em Sistemas para Internet.",
    version="1.0"
)

@app.get("/")
def testar_api():
    return {"mensagem": "A minha API está viva e a funcionar!"}

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

@app.put("/api/projects/{id}/upvote", response_model=schemas.ProjectResponse)
def upvote_project(id: int, db: Session = Depends(get_db)):
    project = db.query(models.ProjectModel).filter(models.ProjectModel.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    project.upvotes += 1
    db.commit()
    db.refresh(project)
    return project

@app.post("/api/projects/{id}/feedbacks", response_model=schemas.FeedbackResponse)
def create_feedback(id: int, feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    project = db.query(models.ProjectModel).filter(models.ProjectModel.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    db_feedback = models.FeedbackModel(
        comment=feedback.comment,
        author=feedback.author,
        rating=feedback.rating,
        project_id=id
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    all_feedbacks = db.query(models.FeedbackModel).filter(models.FeedbackModel.project_id == id).all()
    if all_feedbacks:
        total_score = sum(f.rating for f in all_feedbacks)
        project.average_rating = total_score / len(all_feedbacks)
        db.commit()
        db.refresh(project)
        
    return db_feedback

@app.get("/api/projects", response_model=list[schemas.ProjectResponse])
def list_projects(skip: int = 0, limit: int = 10, technology: str = None, db: Session = Depends(get_db)):
    query = db.query(models.ProjectModel)
    if technology:
        query = query.join(models.ProjectModel.technologies).filter(models.TechnologyModel.name.ilike(f"%{technology}%"))
    return query.offset(skip).limit(limit).all()

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"erro": True, "mensagem": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"erro": True, "mensagem": "Dados inválidos fornecidos", "detalhes": exc.errors()},
    )