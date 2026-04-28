"""Central paths and workflow configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Paths:
    root: Path = PROJECT_ROOT
    raw_dir: Path = PROJECT_ROOT / "data" / "raw"
    processed_dir: Path = PROJECT_ROOT / "data" / "processed"

    metrics_csv: Path = raw_dir / "full_geofresh_gbm_metrics.csv"
    thinned_presences_csv: Path = raw_dir / "thinned_presences.csv"
    continental_predictions_csv: Path = raw_dir / "continental_predictions.csv"

    task1_dir: Path = processed_dir / "task1_qc"
    task2_dir: Path = processed_dir / "task2_projections"
    task3_dir: Path = processed_dir / "task3_realized"


@dataclass(frozen=True)
class ExportConfig:
    suitability_min: float = 0.1


PATHS = Paths()
EXPORT_CONFIG = ExportConfig()
