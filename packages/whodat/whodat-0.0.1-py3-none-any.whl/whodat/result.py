from typing import Any

from pydantic import BaseModel

from whodat.model import WhodatResponse


class SingleRowInfo(BaseModel):
    """Information about the personal ID search for a single row.

    Attributes:
        index_original_df (int): The index of the row in the original dataframe.
        number_of_found_ids (int): The number of personal IDs found for the row. 1 if unique.
        unique_response_step_number (int): The 1-indexed search algorithm that gave a unique result.
            None if no unique result was found.
    """

    index_original_df: int
    number_of_found_ids: int
    unique_response_step_number: int | None


class Result:
    """Result of a Whodat personal ID search."""

    def __init__(self, responses: list[tuple[WhodatResponse, int]]) -> None:
        """Result of a Whodat personal ID search.

        Args:
            responses (list[tuple[WhodatResponse, int]]): List of (responses, index) from Whodat service.
        """
        self.responses = responses
        self._details: list[dict[str, Any]] = self._generate_details()

    def to_list(self, exclude_nones: bool | None = False) -> list[str | None]:
        """Convert the result to a list of personal IDs. By default, returns None if a unique ID was not found.

        Args:
            exclude_nones (bool, optional): Exclude "None" from requests that did not yield a unique result. Defaults to False.

        Returns:
            list[str | None]: _description_
        """
        result: list[str | None] = []
        for response in self.responses:
            found_ids = response[0].found_personal_ids

            if len(found_ids) == 1:
                result.append(found_ids[0])
            elif exclude_nones is False:
                result.append(None)

        return result

    def _generate_details(self) -> list[dict[str, Any]]:
        details = []
        for i, response in enumerate(self.responses):
            found_ids = response[0].found_personal_ids
            number_of_found_ids = len(found_ids)
            unique_response_step_number = (
                response[1] if number_of_found_ids == 1 else None
            )
            details.append(
                SingleRowInfo(
                    index_original_df=i,
                    number_of_found_ids=number_of_found_ids,
                    unique_response_step_number=unique_response_step_number,
                ).model_dump()
            )

        return details

    @property
    def details(self) -> list[dict[str, Any]]:
        """Return detailed information about the personal ID search for each row.

        Returns:
            list[dict[str, Any]]: A list of dictionaries with information about each row's search result.
        """
        return self._details
