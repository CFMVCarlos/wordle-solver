from app.models.schemas import SolveRequest, SolveResponse
from app.services.solver_service import SolverService

class SolverController:
    """
    Controller layer to handle HTTP request logic before delegating to the Service layer.
    """
    
    @staticmethod
    def process_solve_request(request: SolveRequest) -> SolveResponse:
        """
        Processes the solve request payload.
        
        Args:
            request (SolveRequest): The incoming request payload.
            
        Returns:
            SolveResponse: The formatted response payload.
        """
        count, best_guess, remaining = SolverService.solve(request.attempts)
        
        return SolveResponse(
            status="success",
            remaining_words_count=count,
            optimal_guess=best_guess,
            remaining_words=remaining[:100]  # Cap at 100 to prevent massive payloads
        )
