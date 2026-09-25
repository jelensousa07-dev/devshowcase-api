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
    
    # Criar o feedback associado ao projeto
    db_feedback = models.FeedbackModel(
        comment=feedback.comment,
        author=feedback.author,
        rating=feedback.rating,
        project_id=id
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    # Calcular automaticamente a nova nota média do projeto
    all_feedbacks = db.query(models.FeedbackModel).filter(models.FeedbackModel.project_id == id).all()
    if all_feedbacks:
        total_score = sum(f.rating for f in all_feedbacks)
        project.average_rating = total_score / len(all_feedbacks)
        db.commit()
        db.refresh(project)
        
    return db_feedback@app.get("/api/projects", response_model=list[schemas.ProjectResponse])
def list_projects(skip: int = 0, limit: int = 10, technology: str = None, db: Session = Depends(get_db)):
    query = db.query(models.ProjectModel)
    if technology:
        query = query.join(models.ProjectModel.technologies).filter(models.TechnologyModel.name.ilike(f"%{technology}%"))
    return query.offset(skip).limit(limit).all()
    from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

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