from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TARGET_CSV = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "spatial_extraction_targets"
    / "woc_full_geofresh_projection_targets.csv"
)

PROJECTION_DIR = PROJECT_ROOT / "data" / "processed" / "task2_woc_spatial_projections"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "task2_lucian_exports_woc_spatial"

COHORT = [
    ("Austropotamobius bihariensis", "austropotamobius_bihariensis"),
    ("Cambaroides similis", "cambaroides_similis"),
    ("Cambarus eeseeohensis", "cambarus_eeseeohensis"),
    ("Cambarus reburrus", "cambarus_reburrus"),
    ("Cambarus elkensis", "cambarus_elkensis"),
    ("Cambarus lenati", "cambarus_lenati"),
    ("Cambarus hatfieldi", "cambarus_hatfieldi"),
]


def load_target_coords() -> pd.DataFrame:
    cols = ["target_cell_idx", "subc_id", "longitude", "latitude"]
    target = pd.read_csv(TARGET_CSV, usecols=cols)
    return target.drop_duplicates(["target_cell_idx", "subc_id"])


def export_species(species: str, slug: str, target: pd.DataFrame) -> dict:
    projection_path = PROJECTION_DIR / f"{slug}__full_geofresh__gbm__woc_spatial.parquet"
    if not projection_path.exists():
        raise FileNotFoundError(f"Missing projection parquet: {projection_path}")

    df = pd.read_parquet(projection_path)

    merged = df.merge(
        target,
        on=["target_cell_idx", "subc_id"],
        how="left",
        validate="one_to_one",
    )

    if merged[["longitude", "latitude"]].isna().any().any():
        missing = int(merged[["longitude", "latitude"]].isna().any(axis=1).sum())
        raise ValueError(f"{species}: {missing} projected rows missing coordinates")

    out = (
        merged.loc[
            merged["predicted_suitability"] >= 0.1,
            ["longitude", "latitude", "predicted_suitability"],
        ]
        .rename(columns={"predicted_suitability": "suitability"})
        .drop_duplicates(["longitude", "latitude", "suitability"])
        .sort_values(["longitude", "latitude", "suitability"])
        .reset_index(drop=True)
    )

    out_path = OUTPUT_DIR / f"inertia_{slug}.csv"
    out.to_csv(out_path, index=False)

    return {
        "species": species,
        "species_slug": slug,
        "projection_rows_total": len(df),
        "rows_suitability_ge_0_1": len(out),
        "suitability_min_exported": out["suitability"].min() if len(out) else None,
        "suitability_max_exported": out["suitability"].max() if len(out) else None,
        "output_file": str(out_path),
        "important_note": "Projection target is WoC/GeoFRESH occurrence-linked universe, not full continental Hydrography90m.",
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading target coordinates...")
    target = load_target_coords()

    summaries = []
    for species, slug in COHORT:
        print(f"Exporting {species}...")
        summaries.append(export_species(species, slug, target))

    summary = pd.DataFrame(summaries)
    summary_path = OUTPUT_DIR / "task2_lucian_export_summary.csv"
    summary.to_csv(summary_path, index=False)

    print()
    print(f"Wrote summary: {summary_path}")
    print(summary[["species", "projection_rows_total", "rows_suitability_ge_0_1"]].to_string(index=False))


if __name__ == "__main__":
    main()
