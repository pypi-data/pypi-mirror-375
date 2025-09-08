from fastapi import FastAPI

from app.core.database import register_database
from app.domains.company.views import router as company_router
from app.domains.project.views import router as project_router
from app.domains.project.views import task_router

app = FastAPI(
    title='FastAPI Mason',
    version='0.0.0',
    description='FastAPI Mason is a library for building FastAPI applications with Django REST Framework-inspired ViewSets and utilities',
)
register_database(app)

app.include_router(company_router)
app.include_router(project_router)
app.include_router(task_router)
