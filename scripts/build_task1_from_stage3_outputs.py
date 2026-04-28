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
EVAL_DIR = STAGE3_ROOT / "evaluations"

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "task1_qc"
OUTPUT_CSV = OUTPUT_DIR / "endemic_cohort_data_check.csv"

COHORT = [
    ("Austropotamobius bihariensis", "austropotamobius_bihariensis"),
    ("Cambaroides similis", "cambaroides_similis"),
    ("Cambarus eeseeohensis", "cambarus_eeseeohensis"),
    ("Cambarus reburrus", "cambarus_reburrus"),
    ("Cambarus elkensis", "cambarus_elkensis"),
    ("Cambarus lenati", "cambarus_lenati"),
    ("Cambarus hatfieldi", "cambarus_hatfieldi"),
]


def summarize_species(species: str, slug: str) -> dict:
    biomod_path = BIOMOD_DIR / f"{slug}__full_geofresh_biomod_pilot.csv"
    eval_path = EVAL_DIR / f"{slug}__full_geofresh_esm_gbm_evaluations.csv"

    if not biomod_path.exists():
        raise FileNotFoundError(f"Missing BIOMOD input file: {biomod_path}")

    if not eval_path.exists():
        raise FileNotFoundError(f"Missing evaluation file: {eval_path}")

    biomod = pd.read_csv(biomod_path)
    if "resp" not in biomod.columns:
        raise ValueError(f"'resp' column not found in {biomod_path}")

    n_presences_thinned = int((biomod["resp"] == 1).sum())
    n_background_or_absence = int((biomod["resp"] == 0).sum())

    eval_df = pd.read_csv(eval_path)

    required_cols = {"AUC", "TSS", "Boyce", "fit_status", "run"}
    missing_cols = sorted(required_cols - set(eval_df.columns))
    if missing_cols:
        raise ValueError(f"Missing columns in {eval_path}: {missing_cols}")

    ok = eval_df[eval_df["fit_status"].eq("ok")].copy()

    # The files contain one allData/allRun row plus RUN1-RUN5 rows.
    # For the single QC value requested by Lucian, we report the mean over RUN1-RUN5.
    cv = ok[ok["run"].astype(str).str.upper().str.startswith("RUN")].copy()

    if cv.empty:
        raise ValueError(f"No RUN1-RUN5 rows found in {eval_path}")

    return {
        "species": species,
        "species_slug": slug,
        "n_presences_thinned": n_presences_thinned,
        "n_background_or_absence": n_background_or_absence,
        "AUC": cv["AUC"].mean(),
        "TSS": cv["TSS"].mean(),
        "Boyce": cv["Boyce"].mean(),
        "AUC_sd": cv["AUC"].std(),
        "TSS_sd": cv["TSS"].std(),
        "Boyce_sd": cv["Boyce"].std(),
        "n_cv_runs": len(cv),
        "predictor_set": "full_geofresh",
        "model_core": "GBM",
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = [summarize_species(species, slug) for species, slug in COHORT]
    out = pd.DataFrame(rows)

    # Lucian requested these exact simple columns.
    simple = out[
        [
            "species",
            "n_presences_thinned",
            "AUC",
            "TSS",
            "Boyce",
        ]
    ].copy()

    # Keep values readable but not over-rounded.
    simple["AUC"] = simple["AUC"].round(3)
    simple["TSS"] = simple["TSS"].round(3)
    simple["Boyce"] = simple["Boyce"].round(3)

    simple.to_csv(OUTPUT_CSV, index=False)

    detailed_csv = OUTPUT_DIR / "endemic_cohort_data_check_detailed.csv"
    out.to_csv(detailed_csv, index=False)

    print(f"Wrote: {OUTPUT_CSV}")
    print(f"Wrote: {detailed_csv}")
    print()
    print(simple.to_string(index=False))


if __name__ == "__main__":
    main()
