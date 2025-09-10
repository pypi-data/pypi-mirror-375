from data_doctor.cleaner import DataCleaner
from data_doctor.transformer import DataTransformer
from data_doctor.validator import DataValidator
import pandas as pd
from typing import Dict, Any


class DataPipeline:
    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        self.df = df.copy()

    def run_basic_cleaning(self) -> pd.DataFrame:
        """Run core cleaning operations: drop duplicates, 
        fill missing, standardize strings.
        """
        self.df = (
            DataCleaner(self.df)
            .drop_duplicates()
            .fill_missing(strategy="mean")
            .standardize_strings()
            .get_df()
        )
        return self.df

    def run_transformations(self) -> pd.DataFrame:
        """Run numeric and categorical transformations."""
        self.df = (
            DataTransformer(self.df)
            .normalize_numeric()
            .encode_categorical()
            .get_df()
        )
        return self.df

    def validate(self) -> Dict[str, Any]:
        """Return a summary of data validation checks."""
        validator = DataValidator(self.df)
        return {
            "missing": validator.check_missing(),
            "duplicates": validator.check_duplicates(),
            "types": validator.check_types()
        }

    def run_full_pipeline(self) -> pd.DataFrame:
        """Run cleaning, transformations, and return the processed DataFrame.
        """
        self.run_basic_cleaning()
        self.run_transformations()
        return self.df
