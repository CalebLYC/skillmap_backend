from fastapi import APIRouter, status


# Router
router = APIRouter(
    tags=["Auth"],
    dependencies=[],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden"},
    },
)


@router.post(
    "/login",
    # response_model=
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    response_description="Login user",
)
def login():
    return "Login"


@router.post(
    "/register",
    # response_model=
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    response_description="Register user",
)
def login():
    return "Register"
