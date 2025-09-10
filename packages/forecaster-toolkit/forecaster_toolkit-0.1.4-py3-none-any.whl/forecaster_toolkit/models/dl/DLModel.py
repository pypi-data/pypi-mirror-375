from typing import Union

import numpy as np
import pandas as pd
from neuralforecast import NeuralForecast
from neuralforecast.tsdataset import TimeSeriesDataset


class DLModel:
    def __init__(
        self,
    ):
        self.is_fitted = False
        self.nf = None
        self.mode = None
        self.target_column = None

    def _prepare_dataset(
        self, X: pd.DataFrame, target_column: str
    ) -> Union[pd.DataFrame, TimeSeriesDataset]:
        """
        Prepare the dataset for the model

        Parameters
        ----------
        X : pd.DataFrame
            Input dataframe with datetime index
        target_column : str
            Name of the target column

        Returns
        -------
        Union[pd.DataFrame, TimeSeriesDataset]
            Prepared dataset in the format required by the model

        Raises
        ------
        ValueError
            If input dataframe doesn't have a DatetimeIndex
        """
        if not isinstance(X.index, pd.DatetimeIndex):
            raise ValueError("Input dataframe must have a DatetimeIndex")

        dataset = pd.DataFrame(
            {
                "unique_id": 1,
                "ds": X.index,
                "y": X[target_column],
            }
        )

        # Add any additional features
        feature_cols = [col for col in X.columns if col != target_column]
        if feature_cols:
            dataset = pd.concat([dataset, X[feature_cols]], axis=1)

        if self.mode == "manual":
            return dataset

        dataset["available_mask"] = 1

        # Convert datetime to numeric (timestamps)
        dataset["ds_numeric"] = dataset["ds"].astype(np.int64) // 10**9

        # Prepare temporal data
        temporal_cols = ["ds", "y", "available_mask", *feature_cols]
        temporal = dataset[["ds_numeric", "y", "available_mask", *feature_cols]]

        # Create TimeSeriesDataset
        return TimeSeriesDataset(
            temporal=temporal,
            temporal_cols=temporal_cols,
            indptr=np.array([0, len(dataset)]),  # one time series
            y_idx=0,  # 'y' is in the first column after ds_numeric
        )

    def fit(self, X: pd.DataFrame, target_column: str):
        """
        Fit the model

        Parameters
        ----------
        X : pd.DataFrame
            Input dataframe with datetime index
        target_column : str
            Name of the target column

        Raises
        ------
        ValueError
            If mode is not set
        """
        if not self.mode:
            raise ValueError("Mode must be set before fitting the model")

        self.target_column = target_column
        dataset = self._prepare_dataset(X=X, target_column=target_column)

        if self.mode == "manual":
            models = [self.model]

            # Create NeuralForecast instance with minimal parameters
            self.nf = NeuralForecast(models=models, freq=pd.infer_freq(X.index))

            self.nf.fit(dataset)
        elif self.mode == "auto":
            self.model.fit(dataset)

        self.is_fitted = True

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
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")

        if self.mode == "manual":
            forecasts = self.nf.predict()

            # Return predictions as a series with the same index as input
            return pd.Series(
                data=forecasts[self.model.__class__.__name__].values,
                index=forecasts["ds"],
            )
        elif self.mode == "auto":
            predictions_dataset = self._prepare_dataset(
                X=X, target_column=self.target_column
            )
            forecasts = self.model.predict(dataset=predictions_dataset)

            return forecasts
