from typing import Optional

import pandas as pd
from neuralforecast.auto import AutoNHITS
from neuralforecast.models import NHITS

from forecaster_toolkit.models.dl.DLModel import DLModel


class NHITSModel(DLModel):
    def __init__(self, h: int = 12, mode: Optional[str] = "auto"):
        """
        Initialize LSTM model

        Parameters
        ----------
        h : int, default=12
            Forecasting horizon
        mode : str, optional, default="auto"
            Mode of operation: "auto" for automatic model selection or "manual" for manual configuration
        """
        if not isinstance(h, int) or h <= 0:
            raise ValueError("Forecasting horizon 'h' must be a positive integer")

        if mode not in ["auto", "manual"]:
            raise ValueError("Mode must be either 'auto' or 'manual'")

        super().__init__()
        self.h = h
        self.mode = mode

        if mode == "auto":
            self.model = AutoNHITS(h=self.h)
        else:
            self.model = NHITS(
                h=self.h,
            )
        self.target_column = None

    def fit(self, X: pd.DataFrame, target_column: str):
        """
        Fit the LSTM model

        Parameters
        ----------
        X : pd.DataFrame
            Input dataframe with datetime index
        target_column : str
            Name of the target column

        Raises
        ------
        ValueError
            If target_column is not in X.columns
            If X is empty
            If X contains missing values
        """
        if target_column not in X.columns:
            raise ValueError(
                f"Target column '{target_column}' not found in input dataframe"
            )

        if X.empty:
            raise ValueError("Input dataframe is empty")

        if X[target_column].isnull().any():
            raise ValueError("Input dataframe contains missing values in target column")

        return super().fit(X, target_column)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Make predictions using the fitted model

        Parameters
        ----------
        X : pd.DataFrame
            Input dataframe with datetime index

        Returns
        -------
        pd.Series
            Predictions with the same index as input

        Raises
        ------
        ValueError
            If model is not fitted
            If input dataframe is empty
            If input dataframe contains missing values
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")

        if X.empty:
            raise ValueError("Input dataframe is empty")

        if X[self.target_column].isnull().any():
            raise ValueError("Input dataframe contains missing values in target column")

        # Prepare dataset for prediction
        dataset = self._prepare_dataset(X, self.target_column)

        # Make predictions
        forecasts = self.nf.predict(df=dataset)

        # Get the correct model name based on mode
        model_name = "AutoLSTM" if self.mode == "auto" else "LSTM"

        # Return predictions as a series with the same index as input
        return pd.Series(forecasts[model_name].values, index=X.index)
