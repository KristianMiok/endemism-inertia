from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

STAGE3_ROOT = (
    Path.home()
    / "Desktop"
    / "directional-compatibility-crayfish"
    / "data"
    / "processed"
    / "stage3"
)

PROJ_DIR = STAGE3_ROOT / "projections"
TARGET_ENV = STAGE3_ROOT / "target_env_vectors" / "all_targets_env.csv"

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "task2_projections"

COHORT = [
    ("Austropotamobius bihariensis", "austropotamobius_bihariensis", "Europe"),
    ("Cambaroides similis", "cambaroides_similis", "Asia"),
    ("Parastacus pugnax", "parastacus_pugnax", "South America"),
    ("Cambarus eeseeohensis", "cambarus_eeseeohensis", "North America"),
    ("Cambarus reburrus", "cambarus_reburrus", "North America"),
    ("Cambarus elkensis", "cambarus_elkensis", "North America"),
    ("Cambarus lenati", "cambarus_lenati", "North America"),
    ("Cambarus hatfieldi", "cambarus_hatfieldi", "North America"),
]

SUITABILITY_MIN = 0.1


def load_target_coordinates() -> pd.DataFrame:
    cols = ["target_species", "target_cell_idx", "subc_id", "long_or", "lat_or"]
    target = pd.read_csv(TARGET_ENV, usecols=cols)

    # target_cell_idx is only unique within target_species, not globally.
    # The stable join key for Stage 3 projections is therefore:
    # target_species + target_cell_idx + subc_id.
    key_cols = ["target_species", "target_cell_idx", "subc_id"]

    coord_check = (
        target[key_cols + ["long_or", "lat_or"]]
        .drop_duplicates()
        .groupby(key_cols)
        .size()
    )
    bad_coord = int((coord_check > 1).sum())
    if bad_coord:
        raise ValueError(
            f"{bad_coord} projection keys map to multiple coordinate pairs"
        )

    target = target.drop_duplicates(key_cols).copy()

    return target.rename(
        columns={
            "long_or": "longitude",
            "lat_or": "latitude",
        }
    )


def export_species(species: str, slug: str, continent: str, target_coords: pd.DataFrame) -> dict:
    projection_path = PROJ_DIR / f"{slug}__full_geofresh__gbm.parquet"

    if not projection_path.exists():
        raise FileNotFoundError(f"Missing projection file: {projection_path}")

    projection = pd.read_parquet(projection_path)

    required = {
        "source_species",
        "target_species",
        "target_cell_idx",
        "subc_id",
        "predicted_suitability",
        "predictor_set",
        "core",
    }
    missing = sorted(required - set(projection.columns))
    if missing:
        raise ValueError(f"Missing columns in {projection_path}: {missing}")

    merged = projection.merge(
        target_coords[
            [
                "target_species",
                "target_cell_idx",
                "subc_id",
                "longitude",
                "latitude",
            ]
        ],
        on=["target_species", "target_cell_idx", "subc_id"],
        how="left",
        validate="many_to_one",
    )

    if merged["longitude"].isna().any() or merged["latitude"].isna().any():
        n_missing = int(merged["longitude"].isna().sum() + merged["latitude"].isna().sum())
        raise ValueError(f"Missing coordinates after join for {species}: {n_missing}")

    filtered = merged[merged["predicted_suitability"] >= SUITABILITY_MIN].copy()

    out = filtered[["longitude", "latitude", "predicted_suitability"]].rename(
        columns={"predicted_suitability": "suitability"}
    )

    # Multiple target species can point to the same stream reach / coordinate.
    # Lucian requested simple point CSVs for GIS, so keep one row per unique
    # longitude-latitude-suitability combination.
    out = (
        out.drop_duplicates(["longitude", "latitude", "suitability"])
        .sort_values(["longitude", "latitude"])
        .reset_index(drop=True)
    )

    output_path = OUTPUT_DIR / f"inertia_{slug}.csv"
    out.to_csv(output_path, index=False)

    return {
        "species": species,
        "species_slug": slug,
        "continent": continent,
        "projection_file": str(projection_path),
        "n_projection_rows_total": len(projection),
        "n_rows_suitability_ge_0_1": len(out),
        "output_file": str(output_path),
        "note": "Export from Stage 3 matrix-target projections, not independently verified as full continental Hydrography90m projection.",
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    target_coords = load_target_coordinates()

    summaries = []
    for species, slug, continent in COHORT:
        print(f"Exporting {species}...")
        summaries.append(export_species(species, slug, continent, target_coords))

    summary = pd.DataFrame(summaries)
    summary_path = OUTPUT_DIR / "task2_projection_export_summary.csv"
    summary.to_csv(summary_path, index=False)

    print()
    print(f"Wrote summary: {summary_path}")
    print(summary[["species", "n_projection_rows_total", "n_rows_suitability_ge_0_1"]].to_string(index=False))


if __name__ == "__main__":
    main()
