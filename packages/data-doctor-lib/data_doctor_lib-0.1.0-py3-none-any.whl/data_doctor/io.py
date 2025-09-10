import pandas as pd


def read_csv(file_path: str) -> pd.DataFrame:
    """Read a CSV file into a DataFrame."""
    return pd.read_csv(file_path)


def write_csv(df: pd.DataFrame, file_path: str) -> None:
    """Write a DataFrame to a CSV file."""
    df.to_csv(file_path, index=False)