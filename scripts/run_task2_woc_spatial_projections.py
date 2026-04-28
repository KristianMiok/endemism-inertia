from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOURCE_PIPELINE_ROOT = Path.home() / "Desktop" / "directional-compatibility-crayfish"

TARGET_CSV = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "spatial_extraction_targets"
    / "woc_full_geofresh_projection_targets.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "task2_woc_spatial_projections"

COHORT = [
    ("Austropotamobius bihariensis", "austropotamobius_bihariensis"),
    ("Cambaroides similis", "cambaroides_similis"),
    ("Cambarus eeseeohensis", "cambarus_eeseeohensis"),
    ("Cambarus reburrus", "cambarus_reburrus"),
    ("Cambarus elkensis", "cambarus_elkensis"),
    ("Cambarus lenati", "cambarus_lenati"),
    ("Cambarus hatfieldi", "cambarus_hatfieldi"),
]


def run_one(species: str, slug: str, overwrite: bool = False) -> None:
    output_parquet = OUTPUT_DIR / f"{slug}__full_geofresh__gbm__woc_spatial.parquet"

    if output_parquet.exists() and not overwrite:
        print(f"SKIP existing: {output_parquet}")
        return

    cmd = [
        "Rscript",
        "R/03_project_sdm.R",
        "--source-species",
        species,
        "--source-slug",
        slug,
        "--predictor-set",
        "full_geofresh",
        "--core",
        "GBM",
        "--workspace",
        str((SOURCE_PIPELINE_ROOT / "data" / "processed" / "stage3" / "biomod_workspace").absolute()),
        "--target-env-csv",
        str(TARGET_CSV.absolute()),
        "--output-parquet",
        str(output_parquet.absolute()),
    ]

    print("\n" + "=" * 80)
    print(f"Projecting: {species}")
    print(f"Output: {output_parquet}")
    print("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        cmd,
        cwd=SOURCE_PIPELINE_ROOT,
        text=True,
        capture_output=False,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Projection failed for {species} with exit code {result.returncode}")

    if not output_parquet.exists():
        raise FileNotFoundError(f"Projection finished but output missing: {output_parquet}")

    print(f"OK: {output_parquet}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--species-slug", default=None, help="Run only one species slug.")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if not TARGET_CSV.exists():
        raise FileNotFoundError(f"Missing target CSV: {TARGET_CSV}")

    selected = COHORT
    if args.species_slug:
        selected = [x for x in COHORT if x[1] == args.species_slug]
        if not selected:
            raise ValueError(f"Unknown species slug: {args.species_slug}")

    for species, slug in selected:
        run_one(species, slug, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
