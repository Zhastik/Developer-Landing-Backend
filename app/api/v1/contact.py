from fastapi import APIRouter, Depends, Request, status

from app.schemas.contact import ContactCreate, ContactResponse
from app.services.contact_service import ContactService
from app.services.rate_limit_service import RateLimitService

router = APIRouter(prefix="/contact", tags=["Contact"])


def get_contact_service() -> ContactService:
    return ContactService()


def get_rate_limit_service() -> RateLimitService:
    return RateLimitService()


def get_client_key(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if forwarded_for:
        return forwarded_for
    if request.client:
        return request.client.host
    return "unknown"


@router.post("", response_model=ContactResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_contact(
    payload: ContactCreate,
    request: Request,
    contact_service: ContactService = Depends(get_contact_service),
    rate_limit_service: RateLimitService = Depends(get_rate_limit_service),
) -> ContactResponse:
    rate_limit_service.check_contact_limit(get_client_key(request))
    request_id = getattr(request.state, "request_id", None)
    return await contact_service.create_contact(payload, request_id=request_id)
