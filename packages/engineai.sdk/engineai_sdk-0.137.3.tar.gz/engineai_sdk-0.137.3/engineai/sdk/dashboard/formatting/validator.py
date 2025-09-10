"""Formatting validator module."""

from typing import Any

import pandas as pd

from engineai.sdk.dashboard.templated_string import InternalDataField


def validate(
    data: pd.DataFrame | dict[str, Any],
    prefix: InternalDataField | None = None,
    suffix: InternalDataField | None = None,
) -> None:
    """Validate if key or column exists in data.

    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): pandas DataFrame or dict where
            the data is present.
        prefix (Optional[InternalDataField]): Fixed
            text (or key/column data) to be added before axis.
            Defaults to None.
        suffix (Optional[InternalDataField]): Fixed
            text (or key/column data) to be added after axis.
            Defaults to None.
    """
    if prefix is not None:
        prefix.validate(data)
    if suffix is not None:
        suffix.validate(data)
