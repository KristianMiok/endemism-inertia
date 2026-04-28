"""Task implementations for Lucian's requested exports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from crayfish_inertia.cohort import cohort_species_names, species_to_file_stem
from crayfish_inertia.config import EXPORT_CONFIG, PATHS, ExportConfig, Paths
from crayfish_inertia.io import normalize_columns, read_csv_checked, write_csv


def _filter_cohort(df: pd.DataFrame) -> pd.DataFrame:
    cohort = set(cohort_species_names())
    out = df[df["species"].isin(cohort)].copy()
    missing = sorted(cohort - set(out["species"].unique()))
    if missing:
        print("WARNING: These cohort species were not found in the input table:")
        for species in missing:
            print(f"  - {species}")
    return out


def run_task1_qc(paths: Paths = PATHS) -> Path:
    """Create endemic_cohort_data_check.csv.

    Output columns:
    species,n_presences_thinned,AUC,TSS,Boyce
    """
    metrics = read_csv_checked(paths.metrics_csv)
    metrics = normalize_columns(metrics, required=["species", "AUC", "TSS", "Boyce"])

    presences = read_csv_checked(paths.thinned_presences_csv)
    presences = normalize_columns(presences, required=["species", "longitude", "latitude"])

    metrics = _filter_cohort(metrics)
    presences = _filter_cohort(presences)

    n_table = (
        presences.groupby("species", as_index=False)
        .size()
        .rename(columns={"size": "n_presences_thinned"})
    )

    metrics_small = metrics[["species", "AUC", "TSS", "Boyce"]].drop_duplicates("species")
    out = n_table.merge(metrics_small, on="species", how="outer")
    out = out.sort_values("species").reset_index(drop=True)

    output_path = paths.task1_dir / "endemic_cohort_data_check.csv"
    write_csv(out, output_path)
    print(f"Wrote {output_path}")
    return output_path


def run_task2_projection_exports(
    paths: Paths = PATHS,
    config: ExportConfig = EXPORT_CONFIG,
) -> list[Path]:
    """Export one continental suitability CSV per species.

    Each output has columns:
    longitude,latitude,suitability

    Rows are filtered to suitability >= config.suitability_min.
    """
    predictions = read_csv_checked(paths.continental_predictions_csv)
    predictions = normalize_columns(
        predictions,
        required=["species", "longitude", "latitude", "suitability"],
    )
    predictions = _filter_cohort(predictions)

    output_paths: list[Path] = []

    for species in cohort_species_names():
        species_df = predictions[predictions["species"] == species].copy()
        if species_df.empty:
            print(f"WARNING: no prediction rows found for {species}")
            continue

        species_df = species_df[species_df["suitability"] >= config.suitability_min].copy()
        out = species_df[["longitude", "latitude", "suitability"]].sort_values(
            ["longitude", "latitude"]
        )

        output_path = paths.task2_dir / f"inertia_{species_to_file_stem(species)}.csv"
        write_csv(out, output_path)
        output_paths.append(output_path)
        print(f"Wrote {output_path} ({len(out):,} rows)")

    return output_paths


def run_task3_realized_exports(paths: Paths = PATHS) -> list[Path]:
    """Export one realized presence CSV per species.

    Each output has columns:
    longitude,latitude
    """
    presences = read_csv_checked(paths.thinned_presences_csv)
    presences = normalize_columns(presences, required=["species", "longitude", "latitude"])
    presences = _filter_cohort(presences)

    output_paths: list[Path] = []

    for species in cohort_species_names():
        species_df = presences[presences["species"] == species].copy()
        if species_df.empty:
            print(f"WARNING: no realized presence rows found for {species}")
            continue

        out = (
            species_df[["longitude", "latitude"]]
            .drop_duplicates()
            .sort_values(["longitude", "latitude"])
        )

        output_path = paths.task3_dir / f"realized_{species_to_file_stem(species)}.csv"
        write_csv(out, output_path)
        output_paths.append(output_path)
        print(f"Wrote {output_path} ({len(out):,} rows)")

    return output_paths


def run_all() -> None:
    run_task1_qc()
    run_task2_projection_exports()
    run_task3_realized_exports()
