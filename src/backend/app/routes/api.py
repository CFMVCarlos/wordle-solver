from fastapi import APIRouter
from app.models.schemas import SolveRequest, SolveResponse
from app.controllers.solver_controller import SolverController

router = APIRouter(prefix="/api")

@router.post("/solve", response_model=SolveResponse)
def solve_endpoint(request: SolveRequest):
    """
    Endpoint to process Wordle attempts and return suggestions.
    """
    return SolverController.process_solve_request(request)

@router.get("/health")
def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "success", "message": "API is running"}
