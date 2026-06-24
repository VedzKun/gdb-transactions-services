from fastapi import Depends
from app.repositories.transaction_repository import TransactionRepository as FundTransferRepository
from app.repositories.transaction_log_repository import TransactionLogRepository
from app.repositories.transfer_limit_repository import TransferLimitRepository
from app.services.transfer_service import TransferService as FundTransferService
from app.services.deposit_service import DepositService
from app.services.withdraw_service import WithdrawService
from app.services.transaction_log_service import TransactionLogService
from app.services.transfer_limit_service import TransferLimitService

def get_fund_transfer_repository() -> FundTransferRepository:
    return FundTransferRepository()

def get_transaction_log_repository() -> TransactionLogRepository:
    return TransactionLogRepository()

def get_transfer_limit_repository() -> TransferLimitRepository:
    return TransferLimitRepository()

def get_fund_transfer_service(
    repo: FundTransferRepository = Depends(get_fund_transfer_repository),
    log_repo: TransactionLogRepository = Depends(get_transaction_log_repository)
) -> FundTransferService:
    return FundTransferService(repo, log_repo)

def get_deposit_service(
    log_repo: TransactionLogRepository = Depends(get_transaction_log_repository)
) -> DepositService:
    return DepositService(log_repo)

def get_withdraw_service(
    log_repo: TransactionLogRepository = Depends(get_transaction_log_repository)
) -> WithdrawService:
    return WithdrawService(log_repo)

def get_transaction_log_service(
    repo: TransactionLogRepository = Depends(get_transaction_log_repository)
) -> TransactionLogService:
    return TransactionLogService(repo)

def get_transfer_limit_service(
    repo: TransferLimitRepository = Depends(get_transfer_limit_repository)
) -> TransferLimitService:
    return TransferLimitService(repo)
