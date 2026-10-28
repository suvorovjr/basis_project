"""
Constraint names shared by mappings and `constraint_errors.py`.

Declare a name here once, reference it from the mapping and from `CONSTRAINT_TO_ERROR`,
repeat its value as a literal in the revision.
"""

from typing import Final

UQ_PAYMENTS_IDEMPOTENCY_KEY: Final[str] = "uq_payments_idempotency_key"
