import pandas as pd
import pytest

from crayfish_inertia.io import normalize_columns


def test_normalize_coordinate_aliases():
    df = pd.DataFrame(
        {
            "Crayfish_scientific_name": ["A"],
            "lon": [1.0],
            "lat": [2.0],
            "prediction": [0.7],
        }
    )
    out = normalize_columns(df, ["species", "longitude", "latitude", "suitability"])
    assert {"species", "longitude", "latitude", "suitability"}.issubset(out.columns)


def test_missing_required_column_raises():
    df = pd.DataFrame({"species": ["A"]})
    with pytest.raises(ValueError):
        normalize_columns(df, ["species", "longitude"])
