from fastapi import (
    APIRouter,
    Depends,
    status,
    Query,
    Response,
)
from fastapi.responses import (
    JSONResponse,
)
from typing import Annotated
from datetime import timedelta

from api_server.schemas import UserLogin, UserSignup, TokenPayload
from api_server.services import UserService
from api_server.dependencies import (
    get_user_service,
    get_login_form,
    get_token_payload,
)
from api_server.core import database

router = APIRouter(
    prefix='/api/auth',
    tags=['Auth'],
)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    description="Authorizes user and returns session token"
)
async def login_user(
        user_login_data: Annotated[UserLogin, Depends(get_login_form)],
        service: Annotated[
            UserService,
            Depends(get_user_service(database.get_async_session))
        ],
) -> JSONResponse:
    token = await service.login_user(user_data=user_login_data)
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "access_token": token,
            "token_type": "Bearer",
        }
    )
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=timedelta(days=1).days * 86400,
    )
    return response


@router.post(
    "/generate_registration_code",
    status_code=status.HTTP_200_OK,
    description="Receives registration data and returns registration code"
)
async def generate_registration_code(
        user_create_data: Annotated[
            UserSignup,
            Depends(get_login_form)
        ],
        service: Annotated[
            UserService,
            Depends(get_user_service(database.get_async_session))
        ],
) -> JSONResponse:
    registration_code = await service.generate_registration_code(
        user_data=user_create_data
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": registration_code,
            "max_age_sec": 600
        }
    )


@router.post(
    "/activate_registration_code",
    status_code=status.HTTP_201_CREATED,
    description="Receives registration code and completes registration"
)
async def complete_signup(
        tg_chat_id: Annotated[int, Query()],
        code: Annotated[str, Query()],
        service: Annotated[
            UserService,
            Depends(get_user_service(database.get_async_session))
        ],
) -> JSONResponse:
    await service.activate_code(
        code=code,
        tg_chat_id=tg_chat_id,
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Successfully signed up a new user"
        }
    )


@router.get(
    "/check_if_tg_is_binded",
    status_code=status.HTTP_200_OK,
    description="Checks whether the chat id is tied to an existing user"
)
async def check_if_chat_id_used(
        response: Response,
        tg_chat_id: Annotated[int, Query()],
        service: Annotated[
            UserService,
            Depends(get_user_service(database.get_async_session))
        ],
) -> Response:
    tg_chat_id_in_db = await service.check_if_chat_id_used(
        tg_chat_id=tg_chat_id
    )
    if tg_chat_id_in_db:
        response.status_code = status.HTTP_409_CONFLICT
    else:
        response.status_code = status.HTTP_200_OK
    return response


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    description="Сlears the user session"
)
async def logout_user(
        response: Response,
        service: Annotated[
            UserService,
            Depends(get_user_service(database.get_async_session))
        ],
        token_payload: Annotated[
            TokenPayload,
            Depends(get_token_payload)
        ]
) -> Response:
    await service.clear_session(user_id=token_payload.sub)
    response.delete_cookie("access_token")
    response.status_code = status.HTTP_200_OK
    return response
