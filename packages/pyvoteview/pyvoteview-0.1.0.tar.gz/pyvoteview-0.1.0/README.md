# PyVoteview

PyVoteview is a Python package for programmatically accessing and analyzing U.S. Congressional voting records from [Voteview](https://voteview.com/). It provides a simple interface to retrieve, filter, and process roll call data for both the House and Senate across sessions and years.

## Features

- Fetch voting records by Congress number or year
- Retrieve data for a range of sessions or years
- Fast, parallelized data loading using Polars and ThreadPoolExecutor


## Installation

PyVoteview requires Python 3.12+ and [Polars](https://pola.rs/):

```sh
pip install pyvoteview
```

## Quick Start

```python
from pyvoteview.core import get_records_by_congress, get_records_by_year

# Get House voting records for the 117th Congress
df = get_records_by_congress(117, "House")

# Get Senate voting records for the year 2020
df = get_records_by_year(2020, "Senate")

# Get records for a range of sessions
df_range = get_records_by_congress_range(115, 117, "House")
```

All functions return a Polars `DataFrame`.

## API Reference

- `get_records_by_congress(number: int, chamber: Literal["House", "Senate"]) -> DataFrame`
- `get_records_by_congress_range(start_congress_number int, end_congress_number int, chamber: Literal["House", "Senate"]) -> DataFrame`
- `get_records_by_year(year: int, chamber: Literal["House", "Senate"]) -> DataFrame`
- `get_records_by_year_range(start_year: int, end_year: int, chamber: Literal["House", "Senate"]) -> DataFrame`

See [`pyvoteview/core.py`](pyvoteview/core.py) for full documentation.

## License

Licensed under the [Apache License 2.0](LICENSE).

## Acknowledgements

Data provided by [Voteview](https://voteview.com/)
