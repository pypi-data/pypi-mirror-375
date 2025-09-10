"""Spec for Playback Initial State widget."""

from typing import Any

import pandas as pd

from engineai.sdk.dashboard.base import AbstractFactory

from .exceptions import PlaybackItemsValidateNoDataColumnError


class InitialState(AbstractFactory):
    """Spec for InitialState widget."""

    def __init__(
        self,
        *,
        start_frame_id: str | None = None,
        end_frame_id: str | None = None,
    ) -> None:
        """Construct spec for Playback Initial State widget.

        Args:
            start_frame_id: column in Pandas DataFrame to define the
                starting frame.
            end_frame_id: column in Pandas DataFrame to define the
                ending frame.
        """
        super().__init__()
        self.__start_frame_id = start_frame_id
        self.__end_frame_id = end_frame_id

    def validate(
        self,
        *,
        id_column: str,
        data: pd.DataFrame,
    ) -> None:
        """Validates Initial State specs.

        Args:
            id_column: column in data where the frames id is stored.
            data: data associated to the face_path

        Raises:
            PlaybackItemsValidateNoDataColumnError: if start frame id not found in
                data keys
            PlaybackItemsValidateNoDataColumnError: if end frame id  not found in
                data keys
        """
        if (
            self.__start_frame_id is not None
            and id_column in data.columns
            and data[data[id_column].isin([self.__start_frame_id])].empty
        ):
            raise PlaybackItemsValidateNoDataColumnError(
                missing_column_name="Start Frame Id",
                missing_column=self.__start_frame_id,
            )

        if (
            self.__end_frame_id is not None
            and id_column in data.columns
            and data[data[id_column].isin([self.__end_frame_id])].empty
        ):
            raise PlaybackItemsValidateNoDataColumnError(
                missing_column_name="End Frame Id",
                missing_column=self.__end_frame_id,
            )

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "startFrameId": self.__start_frame_id,
            "endFrameId": self.__end_frame_id,
        }
