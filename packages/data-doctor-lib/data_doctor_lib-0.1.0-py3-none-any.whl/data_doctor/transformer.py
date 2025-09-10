from sklearn.preprocessing import StandardScaler, OneHotEncoder
import pandas as pd
from typing import Optional


class DataTransformer:
    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        self.df = df.copy()
        self._scaler: Optional[StandardScaler] = None
        self._encoder: Optional[OneHotEncoder] = None

    def normalize_numeric(self) -> "DataTransformer":
        """Standardize numeric columns using z-score normalization."""
        num_cols = self.df.select_dtypes(include="number").columns
        if len(num_cols) > 0:
            self._scaler = StandardScaler()
            self.df[num_cols] = self._scaler.fit_transform(self.df[num_cols])
        return self

    def encode_categorical(self, drop_first: bool = True) -> "DataTransformer":
        """One-hot encode categorical columns, 
        optionally dropping the first category.
        """
        cat_cols = self.df.select_dtypes(include="object").columns
        if len(cat_cols) > 0:
            self._encoder = OneHotEncoder(
                sparse=False, drop='first' if drop_first else None
                )
            encoded = self._encoder.fit_transform(self.df[cat_cols])
            self.df = self.df.drop(columns=cat_cols)
            self.df = pd.concat(
                [
                    self.df.reset_index(drop=True),
                    pd.DataFrame(
                        encoded, columns=self._encoder.get_feature_names_out(cat_cols)
                        )
                ],
                axis=1
            )
        return self

    def get_df(self) -> pd.DataFrame:
        """Return the transformed DataFrame."""
        return self.df
