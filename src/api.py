from fastapi import FastAPI
from src.todos.controller import router as todos_router
from src.auth.controller import router as auth_router
from src.users.controller import router as users_router
from src.organization.controller import router as org_router
from src.organizationMember.controller import router as org_members_router
from src.project.controller import router as project_router
from src.projectMember.controller import router as project_members_router
from src.translationFile.controller import router as translation_file_router
from src.message.controller import router as message_router

def register_routes(app: FastAPI):
    # app.include_router(todos_router)
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(org_router)
    app.include_router(org_members_router)
    app.include_router(project_router)
    app.include_router(project_members_router)
    app.include_router(translation_file_router)
    app.include_router(message_router)
