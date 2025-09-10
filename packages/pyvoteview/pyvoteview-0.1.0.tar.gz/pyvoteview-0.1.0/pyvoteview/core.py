"""Core functionality of PyVoteview"""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from math import floor
from os import cpu_count
from typing import Literal

from polars import DataFrame, Float32, Int32, col, concat, read_csv

"""
Sequence of events:

1. User selects a congress congress_number and chamber.
2. Choices are formatted into a URL.
3. URL is loaded by Polars.
4. Data is returned in a meaningful way.

Additional questions:
1. We should figure out how to have readable values for stuff like votes,
political party, etc.
2. Pydantic? Could be a fun helper function.  Messy very quickly, though.
"""

CURRENT_YEAR = datetime.now(tz=UTC).year


def _convert_year_to_congress_number(year: int) -> int:
    """
    Converts a year to the corresponding U.S. Congress number.

    Args:
        year: The year to convert.

    Returns:
        The corresponding Congress number.  Assumes the January which comes at
        the tail end of a Congress is actually part of the next Congress.
    """

    return floor((year - 1789) / 2) + 1


CURRENT_CONGRESS_NUMBER = _convert_year_to_congress_number(CURRENT_YEAR)


def _validate_congress_number(congress_number: int) -> None:
    """
    Validate that a number is valid for a Congress.

    Args:
        congress_number: Number to validate.
    """

    if congress_number > CURRENT_CONGRESS_NUMBER:
        err = (
            "This Congress would occur after "
            f"{CURRENT_CONGRESS_NUMBER} ({CURRENT_YEAR})."
        )
        raise ValueError(err)
    if congress_number < 1:
        err = (
            "This Congress couldn't have occurred, "
            "because the 1st Congress started in 1789"
        )
        raise ValueError(err)


def _validate_chamber(chamber: str) -> None:
    """
    Validate that a chamber is either House or Senate.

    Args:
        chamber: Chamber to validate.
    """

    if chamber not in ("House", "Senate"):
        err = (
            "Chamber must be one of House or Senate, "
            f"but {chamber} was entered.  The input is case sensitive."
        )
        raise ValueError(err)


def _format_url(
    congress_number: int, chamber: Literal["House", "Senate"]
) -> str:
    """
    Formats URL to be consistent with Voteview expectation.

    Args:
        congress_number: The number of Congress.
        chamber: The chamber of Congress.

    Returns:
        URL formatted as:
        https://voteview.com/static/data/out/votes/{Chamber}{Number}_votes.csv
    """

    return (
        "https://voteview.com/static/data/out/votes/"
        f"{chamber[0]}{congress_number:03}_votes.csv"
    )


def get_records_by_congress(
    congress_number: int, chamber: Literal["House", "Senate"]
) -> DataFrame:
    """
    Retrieves voting records by congress_number and chamber.

    Args:
        congress_number: Enumeration of which Congress to get.
        chamber: Which chamber of Congress to get.

    Returns:
        Polars DataFrame containing the voting records.
    """

    _validate_congress_number(congress_number)
    _validate_chamber(chamber)

    url = _format_url(congress_number, chamber)

    record = read_csv(url, null_values=["N/A"])

    return record.with_columns(
        col("rollnumber").cast(Int32, strict=False),
        col("icpsr").cast(Int32, strict=False),
        col("cast_code").cast(Int32, strict=False),
        col("prob").cast(Float32, strict=False),
    )


def get_records_by_congress_range(
    start_congress_number: int,
    end_congress_number: int,
    chamber: Literal["House", "Senate"],
) -> DataFrame:
    """
    Retrieves voting records by sessions and chamber.

    Args:
        start_congress_number: The start of the congress_number range.
        end_congress_number: The end of the congress_number range.
        chamber: Which chamber of Congress to get.

    Returns:
        Polars DataFrame containing the voting records for that range.
    """

    if start_congress_number >= end_congress_number:
        err = (
            f"The first number ({start_congress_number}) must be strictly "
            f"less than the last number ({end_congress_number})."
        )
        raise ValueError(err)

    records = []
    with ThreadPoolExecutor(
        max_workers=min(32, (cpu_count() or 1) + 4)
    ) as executor:
        records = list(
            executor.map(
                lambda s: get_records_by_congress(s, chamber),
                range(start_congress_number, end_congress_number + 1),
            )
        )

    return concat(records, how="vertical").sort("congress")


def get_records_by_year(
    year: int, chamber: Literal["House", "Senate"]
) -> DataFrame:
    """
    Retrieves voting records by year and chamber.

    Args:
        year: The year that the congress took place.
        chamber: Which chamber of Congress to get.

    Returns:
        Polars DataFrame containing the voting records.
    """

    congress_number = _convert_year_to_congress_number(year)

    return get_records_by_congress(congress_number, chamber)


def get_records_by_year_range(
    start_year: int, end_year: int, chamber: Literal["House", "Senate"]
) -> DataFrame:
    """
    Retrieves voting records by years and chamber.

    Args:
        start_year: The start of the year range.
        end_year: The end of the year range.
        chamber: Which chamber of Congress to get.

    Returns:
        Polars DataFrame containing the voting records for that range.
    """

    start_congress_number = _convert_year_to_congress_number(start_year)
    end_congress_number = _convert_year_to_congress_number(end_year)

    return get_records_by_congress_range(
        start_congress_number, end_congress_number, chamber
    )
