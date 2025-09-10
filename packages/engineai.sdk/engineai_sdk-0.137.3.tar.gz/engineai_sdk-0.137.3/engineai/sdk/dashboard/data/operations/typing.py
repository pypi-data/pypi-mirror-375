"""Specs for Operations typing."""

from .is_not_null import IsNotNull
from .limit import Limit
from .numeric_condition import NumericCondition
from .order_by import OrderBy

OperationItem = Limit | OrderBy | NumericCondition | IsNotNull
