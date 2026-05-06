from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, conint, constr

app = FastAPI(title="Task 10.2 - request validation")


class UserPayload(BaseModel):
    username: str
    age: conint(gt=18)
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = "Unknown"


class UserAcceptedResponse(BaseModel):
    username: str
    age: int
    email: EmailStr
    phone: str


class ValidationIssue(BaseModel):
    field: str
    message: str
    type: str


class ValidationErrorResponse(BaseModel):
    message: str
    errors: list[ValidationIssue]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    issues = [
        ValidationIssue(
            field=".".join(str(part) for part in error["loc"] if part != "body"),
            message=error["msg"],
            type=error["type"],
        )
        for error in exc.errors()
    ]
    payload = ValidationErrorResponse(message="Payload validation failed.", errors=issues)
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content=payload.model_dump())


@app.post(
    "/users/validate",
    response_model=UserAcceptedResponse,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ValidationErrorResponse}},
)
def validate_user(payload: UserPayload) -> UserAcceptedResponse:
    return UserAcceptedResponse(
        username=payload.username,
        age=payload.age,
        email=payload.email,
        phone=payload.phone or "Unknown",
    )
