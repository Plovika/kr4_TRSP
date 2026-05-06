from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Task 10.1 - custom errors")

DEFAULT_INVENTORY = {"keyboard": 3, "mouse": 10}
DEFAULT_ORDERS = {1: {"id": 1, "item": "keyboard", "quantity": 1}}

INVENTORY = dict(DEFAULT_INVENTORY)
ORDERS = {order_id: order.copy() for order_id, order in DEFAULT_ORDERS.items()}


def reset_state() -> None:
    INVENTORY.clear()
    INVENTORY.update(DEFAULT_INVENTORY)

    ORDERS.clear()
    ORDERS.update({order_id: order.copy() for order_id, order in DEFAULT_ORDERS.items()})


class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int


class ApplicationError(Exception):
    error = "ApplicationError"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InventoryLimitError(ApplicationError):
    error = "InventoryLimitError"
    status_code = status.HTTP_409_CONFLICT


class ResourceNotFoundError(ApplicationError):
    error = "ResourceNotFoundError"
    status_code = status.HTTP_404_NOT_FOUND


class ReservationRequest(BaseModel):
    quantity: int = Field(gt=0)


class ReservationResponse(BaseModel):
    sku: str
    reserved: int
    remaining: int


class OrderResponse(BaseModel):
    id: int
    item: str
    quantity: int


def build_error_response(exc: ApplicationError) -> ErrorResponse:
    return ErrorResponse(error=exc.error, message=exc.message, status_code=exc.status_code)


@app.exception_handler(InventoryLimitError)
async def inventory_error_handler(request: Request, exc: InventoryLimitError) -> JSONResponse:
    print(f"Inventory error on {request.url.path}: {exc.message}")
    payload = build_error_response(exc)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(ResourceNotFoundError)
async def not_found_error_handler(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
    print(f"Resource error on {request.url.path}: {exc.message}")
    payload = build_error_response(exc)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.post(
    "/inventory/{sku}/reserve",
    response_model=ReservationResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def reserve_inventory(sku: str, payload: ReservationRequest) -> ReservationResponse:
    if sku not in INVENTORY:
        raise ResourceNotFoundError(f"Inventory item '{sku}' was not found.")

    if payload.quantity > INVENTORY[sku]:
        raise InventoryLimitError(f"Only {INVENTORY[sku]} item(s) of '{sku}' are available.")

    INVENTORY[sku] -= payload.quantity
    return ReservationResponse(sku=sku, reserved=payload.quantity, remaining=INVENTORY[sku])


@app.get("/orders/{order_id}", response_model=OrderResponse, responses={404: {"model": ErrorResponse}})
def get_order(order_id: int) -> OrderResponse:
    order = ORDERS.get(order_id)
    if order is None:
        raise ResourceNotFoundError(f"Order with id={order_id} was not found.")
    return OrderResponse(**order)
