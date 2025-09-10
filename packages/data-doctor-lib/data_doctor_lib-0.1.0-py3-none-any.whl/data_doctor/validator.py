import pandas as pd
import re
from typing import Dict


class DataValidator:
    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        self.df = df.copy()

    def check_missing(self) -> pd.Series:
        """Return the number of missing values per column."""
        return self.df.isnull().sum()

    def check_duplicates(self) -> int:
        """Return the number of duplicate rows."""
        return self.df.duplicated().sum()

    def check_types(self) -> Dict[str, str]:
        """Return the data types of each column as a dictionary."""
        return self.df.dtypes.astype(str).to_dict()

    def validate_email(self, column: str) -> "DataValidator":
        """Validate email addresses in the specified column, 
        setting invalid ones to None.
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")
        email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
        self.df[column] = self.df[column].apply(
            lambda x: x if pd.isna(x) or re.match(email_pattern, str(x)) else None
        )
        return self

    def get_df(self) -> pd.DataFrame:
        """Return the validated DataFrame."""
        return self.df
