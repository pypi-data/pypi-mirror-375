import shap

from abc import ABC, abstractmethod
from typing import Any, Optional
from pathlib import Path
from typing import Callable, TypeVar, Literal, Protocol
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ArrayLike = np.ndarray | pd.DataFrame | pd.Series


class ShapAbstract(ABC):
    def __init__(
        self, model: Any, X: ArrayLike, feature_names: Optional[list[str]] = None, 
        options: Optional[dict] = None
    ):
        self.model = model
        self.X = X
        self.feature_names = feature_names or getattr(X, "columns", None)
        self.shap_vals = None
        self.options = options  
        self.explainer = self._get_explainer()
        

    @abstractmethod
    def _get_explainer(self):
        """Return a SHAP explainer for the model."""
        pass

    def shap_values_helper(self):
        return self.explainer.shap_values(self.X)

    def shap_values(self) -> Any:
        if self.shap_vals is None:
            self.shap_vals = self.shap_values_helper()
        return self.shap_vals

    def summary_plot(
        self,
        show: bool = False,
        save_path: Optional[str] = None,
        plot_type: str = "layered_violin",
        **kwargs,
    ):
        shap_values = self.shap_values()

        # Automatically handle 3D SHAP values arrays (multi-class)
        if isinstance(shap_values, np.ndarray) and shap_values.ndim == 3 and shap_values.shape[2] == 2:
            # Select positive class (class 1)
            shap_values_to_plot = shap_values[:, :, 1]
        else:
            shap_values_to_plot = shap_values

        shap.summary_plot(
            shap_values_to_plot,
            self.X,
            feature_names=self.feature_names,
            show=show,
            plot_type=plot_type,
            **kwargs,
        )
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")
            plt.close()
        if show:
            plt.show()
        else:
            plt.close()


class ShapAuto(ShapAbstract):
    def _get_explainer(self) -> Any:
        import xgboost
        import lightgbm
        from sklearn.ensemble import (
            RandomForestClassifier,
            RandomForestRegressor,
            GradientBoostingClassifier,
            GradientBoostingRegressor,
        )
        from sklearn.linear_model import LogisticRegression, LinearRegression

        # Tree-based models
        if isinstance(
            self.model,
            (
                xgboost.XGBClassifier,
                xgboost.XGBRegressor,
                lightgbm.LGBMClassifier,
                lightgbm.LGBMRegressor,
                RandomForestClassifier,
                RandomForestRegressor,
                GradientBoostingClassifier,
                GradientBoostingRegressor,
            ),
        ):
            return shap.TreeExplainer(self.model)
        # Linear models
        elif isinstance(self.model, (LogisticRegression, LinearRegression)):
            return shap.LinearExplainer(self.model, self.X)
        else:
            # Fallback to KernelExplainer
            sample_size = 100   
            random_state = 42
            if hasattr(self.options, 'shap_sample_size'):
                sample_size = min(100, self.options.shap_sample_size)

            if hasattr(self.options, 'random_state'):
                random_state = self.options.random_state
            background = self.X.sample(n=min(sample_size, len(self.X)), random_state=random_state) if isinstance(self.X, pd.DataFrame) else self.X[:sample_size]
            return shap.KernelExplainer(self.model.predict, background)


class ShapTree(ShapAbstract):
    def _get_explainer(self):
        return shap.TreeExplainer(self.model)


class ShapLinear(ShapAbstract):
    def _get_explainer(self):
        return shap.LinearExplainer(self.model, self.X)
