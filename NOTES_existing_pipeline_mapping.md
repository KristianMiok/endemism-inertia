# Mapping this project to the existing SDM pipeline

Use this file to record where each input comes from in the main repository.

## Needed input 1: full_geofresh/GBM metrics

Copy or symlink to:

```text
data/raw/full_geofresh_gbm_metrics.csv
```

Required final columns:

```text
species,AUC,TSS,Boyce
```

Candidate source from main pipeline:

```text
/path/to/directional-compatibility-crayfish/data/processed/stage3/qc/per_species_quality.csv
```

Check that the rows are specifically:

```text
predictor_set == "full_geofresh"
algorithm/core == "GBM"
```

## Needed input 2: thinned presences

Copy or symlink to:

```text
data/raw/thinned_presences.csv
```

Required final columns:

```text
species,longitude,latitude
```

Candidate source from main pipeline:

```text
/path/to/stage3/species_exports or model-training presences
```

Important: this must be the same thinned presence set used to train each model.

## Needed input 3: continental predictions

Copy or symlink to:

```text
data/raw/continental_predictions.csv
```

Required final columns:

```text
species,longitude,latitude,suitability
```

Candidate source from main pipeline:

```text
/path/to/stage3/predictions/full_geofresh_gbm_continental.csv
```

Important: these must be continental projections, not only training-region predictions.
