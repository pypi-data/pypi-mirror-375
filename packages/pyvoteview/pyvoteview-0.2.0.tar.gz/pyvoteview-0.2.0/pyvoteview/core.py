"""Core functionality of PyVoteview"""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from math import floor
from os import cpu_count
from typing import Literal

from polars import (
    DataFrame,
    DataType,
    Float32,
    Int32,
    Utf8,
    col,
    concat,
    read_csv,
)

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

VOTEVIEW_SCHEMA: dict[str, type[DataType]] = {
    "congress": Int32,
    "chamber": Utf8,
    "rollnumber": Int32,
    "icpsr": Int32,
    "cast_code": Int32,
    "prob": Float32,
    "state_icpsr": Int32,
    "district_code": Int32,
    "state_abbrev": Utf8,
    "party_code": Int32,
    "occupancy": Int32,
    "last_means": Int32,
    "bioname": Utf8,
    "bioguide_id": Utf8,
    "born": Int32,
    "died": Float32,
    "nominate_dim1": Float32,
    "nominate_dim2": Float32,
    "nominate_log_likelihood": Float32,
    "nominate_geo_mean_probability": Float32,
    "nominate_number_of_votes": Int32,
    "nominate_number_of_errors": Int32,
    "conditional": Utf8,
    "nokken_poole_dim1": Float32,
    "nokken_poole_dim2": Float32,
}
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


def _validate_category(category: str) -> None:
    """
    Validate that a category is either votes or members.

    Args:
        category: Category to validate.
    """

    if category not in ("votes", "members"):
        err = f"{category} was selected, but is not one of: votes, members"
        raise ValueError(err)


def _format_url(
    congress_number: int,
    chamber: Literal["House", "Senate"],
    category: Literal["votes", "members"],
) -> str:
    """
    Formats URL to be consistent with Voteview expectation.

    Args:
        congress_number: The number of Congress.
        chamber: The chamber of Congress.

    Returns:
        URL formatted as:
        voteview.com/static/data/out/{Category}/{Chamber}{Number}{Category}.csv
    """

    _validate_category(category)

    return (
        f"https://voteview.com/static/data/out/{category}/"
        f"{chamber[0]}{congress_number:03}_{category}.csv"
    )


def _cast_columns(df: DataFrame) -> DataFrame:
    """
    Casts columns in a DataFrame to specified types.

    Args:
        df: The Polars DataFrame.
        schema: Dict of column names to Polars types.

    Returns:
        DataFrame with columns cast to specified types.
    """
    return df.with_columns(
        [
            col(name).cast(dtype, strict=False)
            for name, dtype in VOTEVIEW_SCHEMA.items()
        ]
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

    url_votes = _format_url(congress_number, chamber, "votes")
    url_members = _format_url(congress_number, chamber, "members")

    record_votes = read_csv(url_votes, null_values=["N/A"])
    record_members = read_csv(url_members, null_values=["N/A"])

    record = record_votes.join(
        record_members, on=["congress", "chamber", "icpsr"], coalesce=True
    )
    return _cast_columns(record)


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
