"""
Transaction Audit Logger using Context Managers
Module 8: File Handling
"""

import os
from datetime import datetime
from typing import Dict, Any

# CR (M08-CR-01): File Audit Logger using Context Manager
# TODO: Implement a logger `log_transaction_audit(transaction_data: Dict[str, Any])`.
# The function should:
# - Ensure the directory `data` exists.
# - Open a text file `data/transaction_audit.log` in append mode (`a`).
# - Use the python context manager `with open(...) as f:` for safe file handle management.
# - Write the transaction details (timestamp, account number, transaction type, amount, status) as a new line.

class TransactionAuditLogger:
    """
    Helper for writing transaction audits to a file.
    """
    
    @staticmethod
    def log_transaction_audit(transaction_data: Dict[str, Any]) -> None:
        """
        Append a transaction audit log entry to a local file.
        """
        os.makedirs("data", exist_ok=True)
        log_file_path = os.path.join("data", "transaction_audit.log")
        
        timestamp = datetime.utcnow().isoformat()
        account_number = transaction_data.get("account_number", "N/A")
        transaction_type = transaction_data.get("transaction_type", "N/A")
        amount = transaction_data.get("amount", "0.00")
        status = transaction_data.get("status", "N/A")
        
        log_line = f"[{timestamp}] Account: {account_number} | Type: {transaction_type} | Amount: {amount} | Status: {status}\n"
        
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(log_line)
