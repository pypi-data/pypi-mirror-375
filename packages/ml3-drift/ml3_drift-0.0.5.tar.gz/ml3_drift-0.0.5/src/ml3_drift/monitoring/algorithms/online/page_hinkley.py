from typing import Callable

import numpy as np

from ml3_drift.enums.monitoring import DataDimension, DataType, MonitoringType
from ml3_drift.models.monitoring import (
    DriftInfo,
    MonitoringAlgorithmSpecs,
    MonitoringOutput,
)
from ml3_drift.monitoring.base.base_univariate import UnivariateMonitoringAlgorithm
from ml3_drift.monitoring.base.online_monitorning_algorithm import (
    OnlineMonitorningAlgorithm,
)

RIVER = True
try:
    from river.drift.page_hinkley import PageHinkley as RiverPageHinkley
except ModuleNotFoundError:
    RIVER = False


class PageHinkley(OnlineMonitorningAlgorithm, UnivariateMonitoringAlgorithm):
    @classmethod
    def specs(cls) -> MonitoringAlgorithmSpecs:
        return MonitoringAlgorithmSpecs(
            data_dimension=DataDimension.MULTIVARIATE,
            data_type=DataType.MIX,
            monitoring_type=MonitoringType.ONLINE,
        )

    def __init__(
        self,
        callbacks: list[Callable[[DriftInfo | None], None]] | None = None,
        min_instances: int = 30,
        delta: float = 0.002,
        alpha: float = 0.999,
        threshold: int = 50,
        mode: str = "both",
        seed: int | None = None,
        *args,
        **kwargs,
    ) -> None:
        if not RIVER:
            raise ModuleNotFoundError(
                "River library is required for PageHinkley algorithm. Please install it using pip install/ uv add ml3-drift[river]"
            )
        self.min_instances = min_instances
        self.delta = delta
        self.alpha = alpha
        self.threshold = threshold
        self.mode = mode
        self.seed = seed
        self._args = args
        self._kwargs = kwargs
        super().__init__(
            callbacks=callbacks, comparison_size=1
        )  # since we add only one sample per step and river handles building the window internally we set comparison_size to 1

    def _reset_internal_parameters(self):
        self.drift_agent = RiverPageHinkley(
            min_instances=self.min_instances,
            delta=self.delta,
            alpha=self.alpha,
            threshold=self.threshold,
            mode=self.mode,
            *self._args,
            **self._kwargs,
        )

    def _fit(self, X: np.ndarray):
        """Fit the KSWIN algorithm to the data."""
        self._validate(X)
        self.reset_internal_parameters()
        self.is_fitted = True

    def _detect(self):
        self.drift_agent.update(self.comparison_data)
        drift_detected = self.drift_agent.drift_detected
        return MonitoringOutput(drift_detected=drift_detected, drift_info=None)
