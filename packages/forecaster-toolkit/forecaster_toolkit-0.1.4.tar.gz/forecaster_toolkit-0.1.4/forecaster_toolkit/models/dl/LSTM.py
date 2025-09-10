from typing import Optional

import pandas as pd
from neuralforecast.auto import AutoLSTM
from neuralforecast.models import LSTM

from forecaster_toolkit.models.dl.DLModel import DLModel


class LSTMModel(DLModel):
    def __init__(
        self, h: int = 12, mode: Optional[str] = "auto", kwargs: Optional[dict] = None
    ):
        """
        Initialize LSTM model

        Parameters
        ----------
        h : int, default=12
            Forecasting horizon
        """
        super().__init__()
        self.h = h
        if mode == "auto":
            self.model = AutoLSTM(h=self.h, **kwargs)
        elif mode == "manual":
            self.model = LSTM(h=self.h, **kwargs)
        self.target_column = None
        self.mode = mode

    def fit(self, X: pd.DataFrame, target_column: str):
        """
        Fit the LSTM model

        Parameters
        ----------
        X : pd.DataFrame
            Input dataframe with datetime index
        target_column : str
            Name of the target column
        """
        return super().fit(X, target_column)

    def predict(self, X: pd.DataFrame = None) -> pd.Series:
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
        """
        return super().predict(X=X)
