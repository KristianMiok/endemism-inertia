from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

ECO_DIR = Path(
    "/Users/kristianmiok/Desktop/Lucian/Global/Descriptive Paper/Data/Eco Variables/eco_variables_tables"
)

OUT_DIR = PROJECT_ROOT / "data" / "processed" / "spatial_extraction_targets"
OUT_CSV = OUT_DIR / "woc_full_geofresh_projection_targets.csv"
OUT_SUMMARY = OUT_DIR / "woc_full_geofresh_projection_targets_summary.csv"

LOCAL_CLIMATE_COLS = ["l_CLI3", "l_CLI23", "l_CLI19", "l_CLI15", "l_CLI47", "l_CLI59"]
LOCAL_TOPO_COLS = ["l_TOP15", "l_TOP122"]
UPSTREAM_CLIMATE_COLS = ["u_CLI3", "u_CLI23", "u_CLI19", "u_CLI15", "u_CLI47", "u_CLI59"]
UPSTREAM_TOPO_COLS = ["u_TOP15", "u_TOP122"]

ALL_PREDICTORS = (
    LOCAL_CLIMATE_COLS
    + LOCAL_TOPO_COLS
    + UPSTREAM_CLIMATE_COLS
    + UPSTREAM_TOPO_COLS
)


def read_csv(path: Path, cols: list[str]) -> pd.DataFrame:
    print(f"Reading {path.name}...")
    return pd.read_csv(path, usecols=cols)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    coords = read_csv(
        ECO_DIR / "WoC_snapped.csv",
        ["WoCID", "lat_or", "long_or", "lat_snap", "long_snap", "basin_id", "subc_id"],
    )

    l_cli = read_csv(
        ECO_DIR / "GF_l_climate.csv",
        ["WoCID", "basin_id", "subc_id"] + LOCAL_CLIMATE_COLS,
    )

    l_top = read_csv(
        ECO_DIR / "GF_l_topography.csv",
        ["WoCID", "basin_id", "subc_id"] + LOCAL_TOPO_COLS,
    )

    u_cli = read_csv(
        ECO_DIR / "GF_u_climate.csv",
        ["WoCID", "basin_id"] + UPSTREAM_CLIMATE_COLS,
    )

    u_top = read_csv(
        ECO_DIR / "GF_u_topography.csv",
        ["WoCID", "basin_id"] + UPSTREAM_TOPO_COLS,
    )

    print("Joining tables...")
    df = coords.merge(l_cli, on=["WoCID", "basin_id", "subc_id"], how="inner", validate="one_to_one")
    df = df.merge(l_top, on=["WoCID", "basin_id", "subc_id"], how="inner", validate="one_to_one")
    df = df.merge(u_cli, on=["WoCID", "basin_id"], how="inner", validate="one_to_one")
    df = df.merge(u_top, on=["WoCID", "basin_id"], how="inner", validate="one_to_one")

    # Use snapped coordinates for projection targets where available; fall back to original coordinates.
    df["longitude"] = df["long_snap"].fillna(df["long_or"])
    df["latitude"] = df["lat_snap"].fillna(df["lat_or"])

    # Deduplicate to one row per stream segment / coordinate / predictor combination.
    before = len(df)
    df = (
        df[
            [
                "WoCID",
                "longitude",
                "latitude",
                "basin_id",
                "subc_id",
                *ALL_PREDICTORS,
            ]
        ]
        .drop_duplicates(["subc_id", "longitude", "latitude"])
        .reset_index(drop=True)
    )
    after_dedup = len(df)

    # Required by the existing R projection script.
    # This is not a biological species; it labels the target universe.
    df["target_species"] = "WoC_GeoFRESH_available_cells"
    df["target_cell_idx"] = range(len(df))
    df["resp"] = 1

    missing_predictors = df[ALL_PREDICTORS].isna().any(axis=1)
    n_missing = int(missing_predictors.sum())

    complete = df[~missing_predictors].copy()

    complete.to_csv(OUT_CSV, index=False)

    summary = pd.DataFrame(
        [
            {
                "target_table": str(OUT_CSV),
                "rows_before_dedup": before,
                "rows_after_dedup": after_dedup,
                "rows_complete_predictors": len(complete),
                "rows_dropped_missing_predictors": n_missing,
                "unique_subc_id": complete["subc_id"].nunique(),
                "unique_basin_id": complete["basin_id"].nunique(),
                "longitude_min": complete["longitude"].min(),
                "longitude_max": complete["longitude"].max(),
                "latitude_min": complete["latitude"].min(),
                "latitude_max": complete["latitude"].max(),
                "important_note": "WoC/GeoFRESH occurrence-linked target universe, not all continental Hydrography90m reaches.",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote: {OUT_CSV}")
    print(f"Wrote: {OUT_SUMMARY}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
