from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

ECO_DIR = Path(
    "/Users/kristianmiok/Desktop/Lucian/Global/Descriptive Paper/Data/Eco Variables/eco_variables_tables"
)
CONTINENT_FILE = (
    Path.home()
    / "Desktop"
    / "directional-compatibility-crayfish"
    / "data"
    / "processed"
    / "occurrence_country_continent_join.csv"
)

TARGET_CSV = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "spatial_extraction_targets"
    / "woc_full_geofresh_projection_targets.csv"
)

PROJECTION_DIR = PROJECT_ROOT / "data" / "processed" / "task2_woc_spatial_projections"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "task2_lucian_exports_continent_filtered"

COHORT = [
    ("Austropotamobius bihariensis", "austropotamobius_bihariensis", "Europe"),
    ("Cambaroides similis", "cambaroides_similis", "Asia"),
    ("Cambarus eeseeohensis", "cambarus_eeseeohensis", "North America"),
    ("Cambarus reburrus", "cambarus_reburrus", "North America"),
    ("Cambarus elkensis", "cambarus_elkensis", "North America"),
    ("Cambarus lenati", "cambarus_lenati", "North America"),
    ("Cambarus hatfieldi", "cambarus_hatfieldi", "North America"),
]


def build_woc_continent_map() -> pd.DataFrame:
    """Attach continent labels to WoCID by row-order validation.

    `occurrence_country_continent_join.csv` lacks WoCID but has the same row count
    and original coordinates as WoC_snapped.csv. We validate row-order coordinate
    agreement before assigning WoCID.
    """
    woc = pd.read_csv(ECO_DIR / "WoC_snapped.csv", usecols=["WoCID", "long_or", "lat_or"])
    cont = pd.read_csv(
        CONTINENT_FILE,
        usecols=["long_or", "lat_or", "country_joined", "continent_joined"],
    )

    if len(woc) != len(cont):
        raise ValueError(f"Row-count mismatch: WoC={len(woc)} continent={len(cont)}")

    same_long = np.isclose(woc["long_or"], cont["long_or"], equal_nan=True)
    same_lat = np.isclose(woc["lat_or"], cont["lat_or"], equal_nan=True)
    n_match = int((same_long & same_lat).sum())

    if n_match != len(woc):
        raise ValueError(
            f"Row-order coordinate validation failed: {n_match}/{len(woc)} rows match"
        )

    out = pd.DataFrame(
        {
            "WoCID": woc["WoCID"],
            "country_joined": cont["country_joined"],
            "continent_joined": cont["continent_joined"],
        }
    )
    return out


def load_target_coords_with_continent() -> pd.DataFrame:
    target = pd.read_csv(
        TARGET_CSV,
        usecols=["WoCID", "target_cell_idx", "subc_id", "longitude", "latitude"],
    ).drop_duplicates(["target_cell_idx", "subc_id"])

    cont = build_woc_continent_map()

    merged = target.merge(cont, on="WoCID", how="left", validate="many_to_one")

    missing = int(merged["continent_joined"].isna().sum())
    if missing:
        print(f"WARNING: {missing} target rows have missing continent_joined")

    return merged


def export_species(species: str, slug: str, continent: str, target: pd.DataFrame) -> dict:
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

    before_continent = len(merged)
    merged = merged[merged["continent_joined"] == continent].copy()
    after_continent = len(merged)

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
        "continent_filter": continent,
        "projection_rows_total": before_continent,
        "rows_in_continent": after_continent,
        "rows_suitability_ge_0_1": len(out),
        "suitability_min_exported": out["suitability"].min() if len(out) else None,
        "suitability_max_exported": out["suitability"].max() if len(out) else None,
        "output_file": str(out_path),
        "important_note": "Projection target is continent-filtered WoC/GeoFRESH occurrence-linked universe, not full all-reach Hydrography90m.",
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading target coordinates and continent labels...")
    target = load_target_coords_with_continent()

    print("\nTarget continent counts:")
    print(target["continent_joined"].value_counts(dropna=False).to_string())

    summaries = []
    for species, slug, continent in COHORT:
        print(f"\nExporting {species} ({continent})...")
        summaries.append(export_species(species, slug, continent, target))

    summary = pd.DataFrame(summaries)
    summary_path = OUTPUT_DIR / "task2_lucian_export_summary.csv"
    summary.to_csv(summary_path, index=False)

    print()
    print(f"Wrote summary: {summary_path}")
    print(
        summary[
            [
                "species",
                "continent_filter",
                "rows_in_continent",
                "rows_suitability_ge_0_1",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
