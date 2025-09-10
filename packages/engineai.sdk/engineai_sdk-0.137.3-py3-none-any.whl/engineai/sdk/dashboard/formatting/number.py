"""Formatting spec for numbers."""

import enum
from typing import Any

import pandas as pd

from engineai.sdk.dashboard.formatting import validator
from engineai.sdk.dashboard.formatting.base import BaseNumberFormatting
from engineai.sdk.dashboard.links.typing import GenericLink
from engineai.sdk.dashboard.templated_string import DataField
from engineai.sdk.dashboard.templated_string import InternalDataField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings


class NumberScale(enum.Enum):
    """Scales to format numbers.

    Description of different scaling options available for formatting numbers.

    Attributes:
        BASE (str): No scale applied.
        PERCENTAGE (str): Numbers are multiplied by 100 and a suffix % is added.
        BASISPOINT (str): Numbers are multiplied by 10000 and a suffix bps is added.
        PIP (str): Numbers are multiplied by 1000000 and a suffix pip is added.
        THOUSAND (str): Numbers are divided by 1000 and suffix K is added.
        MILLION (str): Numbers are divided by 1e6 and suffix M is added.
        BILLION (str): Numbers are divided by 1e9 and suffix Bn is added.
        DYNAMIC_ABSOLUTE (str): Scale is dynamically detected based on range of values.
        DYNAMIC_RELATIVE (str): Apply BASISPOINT if median < 0.01, PERCENTAGE otherwise.
    """

    BASE = "BASE"  # no scale applied
    PERCENTAGE = "PERCENTAGE"  # numbers are multiplied by 100 and a suffix % is added
    BASISPOINT = (
        "BASISPOINT"  # numbers are multiplied by 10000 and a suffix bps is added
    )
    PIP = "PIP"  # numbers are multiplied by 1000000 and a suffix pip is added
    THOUSAND = "THOUSAND"  # numbers are divided by 1000 and suffix K is added
    MILLION = "MILLION"  # numbers are divided by 1e6 and suffix M is added
    BILLION = "BILLION"  # numbers are divided by 1e9 and suffix Bn is added
    DYNAMIC_ABSOLUTE = (
        "DYNAMIC_ABSOLUTE"  # scale is dynamically detected based on range of values
    )
    DYNAMIC_RELATIVE = "DYNAMIC_RELATIVE"  # apply Basis point if median < 0.01
    # apply Percentage otherwise


class NumberFormatting(BaseNumberFormatting):
    """Numeric value formatting.

    Description for formatting numeric values, providing options for scale,
    decimal places, prefix, suffix, and displaying positive sign.
    """

    _INPUT_KEY = "number"

    def __init__(
        self,
        *,
        scale: NumberScale | GenericLink = NumberScale.DYNAMIC_ABSOLUTE,
        decimals: int | None = None,
        prefix: TemplatedStringItem | DataField | None = None,
        suffix: TemplatedStringItem | DataField | None = None,
        show_positive_sign: bool = False,
    ) -> None:
        """Constructor for NumberFormatting.

        Args:
            scale: scale used to format number if is type NumberScale. For example, if
                NumberScale.THOUSAND, number is divided by 1_000 and a suffix "K" is
                added. If is type TemplatedStringItem, this variable allow formatting
                to be dynamically.
                Defaults to NumberScale.DYNAMIC_ABSOLUTE (formats K, M, Bn), but
                not percentage or basis point values.
            decimals: number of decimal places to show after adjusting for scale.
                Defaults to 0 if scale is Dynamic Absolute, Millions or Thousands.
                Defaults to 2 for the remaining scales.
            prefix: Fixed text to be added before number. Cannot be defined if
                prefix_key is used.
            suffix: Fixed text to be added after number. Cannot be defined if
                suffix_key is used.
            show_positive_sign: Flag to activate the plus sign in positive
                number values.
        """
        super().__init__()
        self.__scale = scale
        self.__decimals = decimals
        self.__prefix = InternalDataField(prefix) if prefix else None
        self.__suffix = InternalDataField(suffix) if suffix else None
        self.__show_positive_sign = show_positive_sign

    @property
    def decimals(self) -> int | None:
        """Return the decimals value."""
        if self.__decimals is not None:
            return self.__decimals
        if self.__scale == NumberScale.DYNAMIC_ABSOLUTE:
            return None
        if self.__scale in [
            NumberScale.MILLION,
            NumberScale.THOUSAND,
        ]:
            return 0
        return 2

    @decimals.setter
    def decimals(self, decimals: int | None) -> None:
        self.__decimals = decimals

    @property
    def scale(self) -> NumberScale | GenericLink:
        """Return the scale value."""
        return self.__scale

    def validate(self, data: pd.DataFrame | dict[str, Any]) -> None:
        """Validate if key or column exists in data.

        Args:
            data (Union[pd.DataFrame, Dict[str, Any]]): pandas DataFrame or dict where
                the data is present.
        """
        validator.validate(data=data, prefix=self.__prefix, suffix=self.__suffix)

    def build(self) -> dict[str, Any]:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API
        """
        return {
            "scale": self.scale.value if isinstance(self.scale, NumberScale) else None,
            "scaleOverrideVariable": (
                build_templated_strings(items=self.__scale)
                if not isinstance(self.__scale, NumberScale)
                else None
            ),
            "decimals": self.decimals,
            "prefix": self.__prefix.build() if self.__prefix else None,
            "suffix": self.__suffix.build() if self.__suffix else None,
            "showPositiveSign": self.__show_positive_sign,
        }
