from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api_server.config import settings
from api_server.routers import auth_router
from api_server.exceptions import (
    NoSuchUserInDBException,
    WrongPasswordException,
    UserAlreadyExistException,
    InvalidCodeException,
)

allowed_origins = ["*"]


app = FastAPI(
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.exception_handler(NoSuchUserInDBException)
async def handle_no_such_user_exception(request: Request, exc: NoSuchUserInDBException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content="User with such username doesn't exists",
        headers={"WWW-Authenticate": "Bearer"}
    )


@app.exception_handler(WrongPasswordException)
async def handle_wrong_pass_exception(request: Request, exc: WrongPasswordException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content="User with such username doesn't exists",
        headers={"WWW-Authenticate": "Bearer"}
    )


@app.exception_handler(UserAlreadyExistException)
async def handle_user_already_exist_exception(request: Request, exc: UserAlreadyExistException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content="User with such username already exists",
        headers={"WWW-Authenticate": "Bearer"}
    )


@app.exception_handler(InvalidCodeException)
async def handle_invalid_code_exception(request: Request, exc: InvalidCodeException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content="Invalid code provided",
        headers={"WWW-Authenticate": "Bearer"}
    )


if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=settings.API_HOST,
        port=settings.API_PORT,
    )
