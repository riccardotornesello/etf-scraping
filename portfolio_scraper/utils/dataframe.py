from enum import Enum
from dataclasses import dataclass
from typing import Callable

import pandas as pd


class ColumnType(str, Enum):
    STRING = "string"
    NUMERIC = "numeric"


@dataclass
class Column:
    source: str | None = None
    col_type: ColumnType = ColumnType.STRING
    mapper: dict[str, str] | None = None
    formatter: Callable | None = None


def map_columns(
    columns: dict[str, Column],
    columns_names: dict[str, str],
) -> dict[str, Column]:
    for col in columns:
        if col in columns_names:
            columns[col].source = columns_names[col]
    return columns


def prepare_dataframe(
    df: pd.DataFrame,
    columns: dict[str, Column],
    index_col: str | None = None,
    all_columns: list[str] | None = None,
) -> pd.DataFrame:
    # Rename columns to standard names if source is specified
    df = df.rename(
        columns={v.source: k for k, v in columns.items() if v.source is not None}
    )

    # Keep only the columns we care about
    df = df.reindex(columns=set(c for c in columns.keys() if c))

    # Drop rows where all values are NaN
    df = df.dropna(how="all")

    # Apply formatting
    for col, col_info in columns.items():
        if col_info.formatter:
            df[col] = col_info.formatter(df[col])

    # Convert numeric columns to numeric types, coercing errors to NaN
    numeric_columns = [
        col
        for col, col_info in columns.items()
        if col_info.col_type == ColumnType.NUMERIC
    ]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)

    # Convert string columns to uppercase
    string_columns = [
        col
        for col, col_info in columns.items()
        if col_info.col_type == ColumnType.STRING
    ]
    df[string_columns] = df[string_columns].apply(
        lambda col: col.astype(str).str.upper()
    )

    # Apply mapping to columns if specified
    for col, col_info in columns.items():
        if col_info.mapper:
            df[col] = df[col].map(col_info.mapper)

    # Add any additional columns with NaN values if specified
    if all_columns:
        for col in all_columns:
            if col not in df.columns:
                df[col] = pd.NA

    # Set index if specified
    if index_col:
        df = df.set_index(index_col)

    return df
