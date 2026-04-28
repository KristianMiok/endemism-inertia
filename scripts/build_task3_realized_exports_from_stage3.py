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

BIOMOD_DIR = STAGE3_ROOT / "biomod_inputs"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "task3_realized"

COHORT = [
    ("Austropotamobius bihariensis", "austropotamobius_bihariensis"),
    ("Cambaroides similis", "cambaroides_similis"),
    ("Cambarus eeseeohensis", "cambarus_eeseeohensis"),
    ("Cambarus reburrus", "cambarus_reburrus"),
    ("Cambarus elkensis", "cambarus_elkensis"),
    ("Cambarus lenati", "cambarus_lenati"),
    ("Cambarus hatfieldi", "cambarus_hatfieldi"),
]


def export_species(species: str, slug: str) -> dict:
    input_path = BIOMOD_DIR / f"{slug}__full_geofresh_biomod_pilot.csv"

    if not input_path.exists():
        raise FileNotFoundError(f"Missing BIOMOD input file: {input_path}")

    df = pd.read_csv(input_path)

    required = {"resp", "long_or", "lat_or"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing columns in {input_path}: {missing}")

    pres = df[df["resp"] == 1].copy()

    out = (
        pres[["long_or", "lat_or"]]
        .rename(columns={"long_or": "longitude", "lat_or": "latitude"})
        .drop_duplicates()
        .sort_values(["longitude", "latitude"])
        .reset_index(drop=True)
    )

    output_path = OUTPUT_DIR / f"realized_{slug}.csv"
    out.to_csv(output_path, index=False)

    return {
        "species": species,
        "species_slug": slug,
        "n_realized_points": len(out),
        "input_file": str(input_path),
        "output_file": str(output_path),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    summaries = []
    for species, slug in COHORT:
        print(f"Exporting {species}...")
        summaries.append(export_species(species, slug))

    summary = pd.DataFrame(summaries)
    summary_path = OUTPUT_DIR / "task3_realized_export_summary.csv"
    summary.to_csv(summary_path, index=False)

    print()
    print(f"Wrote summary: {summary_path}")
    print(summary[["species", "n_realized_points"]].to_string(index=False))


if __name__ == "__main__":
    main()
