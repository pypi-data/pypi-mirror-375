from typing import Literal
import pandas as pd
from .validator import DataValidator


class DataCleaner:
    def __init__(self, df: pd.DataFrame):
        """Initialize with a pandas DataFrame."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        self.df = df.copy()

    def drop_duplicates(self) -> "DataCleaner":
        """Remove duplicate rows from the DataFrame."""
        self.df = self.df.drop_duplicates()
        return self

    def fill_missing(
        self, strategy: Literal["mean", "median"] = "mean"
    ) -> "DataCleaner":
        """Fill missing numeric values with a specified strategy (mean or median)."""
        for col in self.df.select_dtypes(include="number"):
            if strategy == "mean":
                self.df[col] = self.df[col].fillna(self.df[col].mean())
            elif strategy == "median":
                self.df[col] = self.df[col].fillna(self.df[col].median())
        return self

    def standardize_strings(self) -> "DataCleaner":
        """Trim whitespace and lowercase all string columns."""
        for col in self.df.select_dtypes(include="object"):
            self.df[col] = self.df[col].astype(str).str.strip().str.lower()
        return self

    def run_email_validation(self, column: str) -> "DataCleaner":
        """Validate email addresses in the specified column using DataValidator."""
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")
        validator = DataValidator(self.df)
        self.df = validator.validate_email(column).get_df()
        return self

    def get_df(self) -> pd.DataFrame:
        """Return the current state of the DataFrame."""
        return self.df.copy()
