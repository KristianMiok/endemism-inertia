"""Input/output helpers with light column normalization."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


COLUMN_ALIASES = {
    "species": ["species", "Species", "Crayfish_scientific_name", "taxon", "scientific_name"],
    "longitude": ["longitude", "lon", "x", "long", "long_or", "decimalLongitude"],
    "latitude": ["latitude", "lat", "y", "lat_or", "decimalLatitude"],
    "suitability": ["suitability", "prediction", "pred", "suit", "score"],
    "AUC": ["AUC", "auc", "AUCroc", "aucroc", "mean_AUC", "mean_auc"],
    "TSS": ["TSS", "tss", "mean_TSS", "mean_tss"],
    "Boyce": ["Boyce", "boyce", "mean_Boyce", "mean_boyce"],
}


def read_csv_checked(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Input file not found: {path}\n"
            "Add the file to data/raw/ or update the path in src/crayfish_inertia/config.py."
        )
    return pd.read_csv(path)


def normalize_columns(df: pd.DataFrame, required: list[str]) -> pd.DataFrame:
    """Rename common column variants to canonical names and validate required columns."""
    rename_map: dict[str, str] = {}

    for canonical in required:
        aliases = COLUMN_ALIASES.get(canonical, [canonical])
        match = next((col for col in aliases if col in df.columns), None)
        if match is None:
            raise ValueError(
                f"Required column '{canonical}' not found. "
                f"Accepted aliases: {aliases}. Available columns: {list(df.columns)}"
            )
        rename_map[match] = canonical

    return df.rename(columns=rename_map)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
