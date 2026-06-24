import logging
import sys
from decimal import Decimal
from typing import Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, Depends
from app.models.enums import TransferMode
from app.services.transfer_service import TransferService as FundTransferService
from app.dependencies.providers import get_fund_transfer_service
from app.exceptions.transaction_exceptions import TransactionException

# Import authorization dependencies from Auth Service
auth_service_path = str(Path(__file__).parent.parent.parent.parent / "auth_service" / "app")
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)

try:
    from security.auth_dependencies import (
        require_manager_or_teller_dependency,
    )
    from security.jwt_validation import JWTValidator
except ImportError:
    # Fallback path
    auth_service_parent = str(Path(__file__).parent.parent.parent.parent / "auth_service")
    if auth_service_parent not in sys.path:
        sys.path.insert(0, auth_service_parent)
    from app.security.auth_dependencies import (
        require_manager_or_teller_dependency,
    )
    from app.security.jwt_validation import JWTValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["transfers"])


@router.post(
    "/transfers",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Transfer successful"},
        400: {"description": "Invalid input or limit exceeded"},
        401: {"description": "Unauthorized - missing/invalid token or invalid PIN"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "Account not found"},
        503: {"description": "Service unavailable"},
    },
)
async def transfer_funds(
    from_account: int,
    to_account: int,
    amount: float,
    pin: str,
    transfer_mode: str = "NEFT",
    description: str = None,
    claims: Dict[str, Any] = Depends(require_manager_or_teller_dependency),
    service: FundTransferService = Depends(get_fund_transfer_service)
) -> dict:
    """
    Transfer funds between two accounts.
    """
    try:
        # Get user info from JWT
        user_role = JWTValidator.get_role(claims)
        login_id = JWTValidator.get_login_id(claims)
        
        logger.info(
            f"💳 Transfer request by {login_id} ({user_role}) - From: {from_account}, "
            f"To: {to_account}, Amount: ₹{amount}"
        )

        # Determine transfer mode
        transfer_mode_enum = TransferMode[transfer_mode.upper()] if transfer_mode else TransferMode.NEFT

        # Call transfer service
        result = await service.process_transfer(
            from_account=from_account,
            to_account=to_account,
            amount=Decimal(str(amount)),
            pin=pin,
            transfer_mode=transfer_mode_enum,
            description=description,
        )

        logger.info(
            f"✅ Transfer successful by {login_id} - From: {from_account}, "
            f"To: {to_account}"
        )

        return result

    except TransactionException as e:
        logger.warning(f"⚠️ Transfer failed: {e.error_code} - {e.message}")
        raise HTTPException(
            status_code=e.http_code,
            detail={"error_code": e.error_code, "message": e.message},
        )

    except Exception as e:
        logger.error(f"❌ Unexpected error during transfer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"},
        )
