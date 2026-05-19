from fastapi import APIRouter

from app.schemas.system import ReconstructionReadinessResponse
from app.services.reconstruction_toolchain import ReconstructionToolchainService


router = APIRouter(prefix="/system", tags=["system"])


@router.get("/reconstruction-readiness", response_model=ReconstructionReadinessResponse)
def reconstruction_readiness() -> ReconstructionReadinessResponse:
    readiness = ReconstructionToolchainService().check()
    return ReconstructionReadinessResponse.model_validate(readiness.to_dict())
