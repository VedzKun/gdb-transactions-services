"""
Transaction Business Logic - Sorting Helper
Module 5: Collections
"""

from typing import List, Dict, Any

# CR (M05-CR-01): Transactions List Sorting Logic
# TODO: Implement a sorting helper `sort_transactions(transactions, key, reverse)`.
# The function should:
# - Accept a list of dictionaries representing transaction logs.
# - Validate that the `key` exists in the log dictionary (e.g. 'amount', 'created_at', 'transaction_type').
# - Sort the list in-place or return a new sorted list based on the key.
# - Support reverse ordering (descending) via the `reverse` parameter.

# TODO: [M05-CR-01] FEATURE: Add functionality to sort the transaction dictionaries in memory based on the provided key.
def sort_transactions(
    transactions: List[Dict[str, Any]], 
    key: str = "id", 
    reverse: bool = False
) -> List[Dict[str, Any]]:
    """
    Sort transaction records in memory based on the provided key.
    """
    if not transactions:
        return []
    
    for tx in transactions:
        if key not in tx:
            raise ValueError(f"Key '{key}' not found in transaction record")
            
    return sorted(transactions, key=lambda x: x[key], reverse=reverse)
