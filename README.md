# Crayfish Endemism Inertia

PyCharm-ready Python project for the narrow-endemic crayfish SDM export workflow requested by Lucian.

Working concept:

> For narrow-endemic crayfish, do continental SDM projections predict suitable freshwater habitat beyond the realized native range?

This repository is designed to produce three deliverables:

1. `endemic_cohort_data_check.csv`
2. `inertia_{species_name}.csv` files with `longitude, latitude, suitability`
3. `realized_{species_name}.csv` files with `longitude, latitude`

The project is intentionally lightweight. It does **not** refit SDMs. It packages outputs from the existing directional-compatibility / SDM pipeline.

---

## Project structure

```text
crayfish-endemism-inertia/
├── data/
│   ├── raw/                         # input files copied or symlinked from the main pipeline
│   └── processed/
│       ├── task1_qc/
│       ├── task2_projections/
│       └── task3_realized/
├── scripts/
│   ├── run_task1_qc.py
│   ├── run_task2_projection_exports.py
│   └── run_task3_realized_exports.py
├── src/
│   └── crayfish_inertia/
│       ├── cohort.py
│       ├── config.py
│       ├── io.py
│       ├── tasks.py
│       └── cli.py
├── tests/
├── pyproject.toml
├── .gitignore
└── README.md
```

---

## Setup in PyCharm

1. Open this folder in PyCharm.
2. Create a virtual environment with Python 3.11 or newer.
3. Install the project:

```bash
pip install -e ".[dev]"
```

4. Run a smoke test:

```bash
python -m crayfish_inertia --help
```

---

## Expected input files

Put or symlink the relevant files from the main SDM pipeline into `data/raw/`.

The starter code assumes three kinds of input tables:

### 1. Model metrics table

Default path:

```text
data/raw/full_geofresh_gbm_metrics.csv
```

Expected columns:

```text
species,AUC,TSS,Boyce
```

Optional accepted variants:

```text
auc,tss,boyce
AUCroc,TSS,boyce
```

### 2. Thinned presences table

Default path:

```text
data/raw/thinned_presences.csv
```

Expected columns:

```text
species,longitude,latitude
```

Accepted coordinate variants include:

```text
lon,lat
x,y
long_or,lat_or
```

### 3. Continental projection table

Default path:

```text
data/raw/continental_predictions.csv
```

Expected columns:

```text
species,longitude,latitude,suitability
```

Accepted suitability variants include:

```text
prediction
pred
suit
```

This can be one large table or you can later adapt `tasks.py` to read one file per species.

---

## Task 1: cohort QC table

```bash
python scripts/run_task1_qc.py
```

Output:

```text
data/processed/task1_qc/endemic_cohort_data_check.csv
```

Columns:

```text
species,n_presences_thinned,AUC,TSS,Boyce
```

---

## Task 2: continental projection exports

```bash
python scripts/run_task2_projection_exports.py
```

Output:

```text
data/processed/task2_projections/inertia_{species_name}.csv
```

Each file has:

```text
longitude,latitude,suitability
```

Rows are filtered to:

```text
suitability >= 0.1
```

---

## Task 3: realized presence exports

```bash
python scripts/run_task3_realized_exports.py
```

Output:

```text
data/processed/task3_realized/realized_{species_name}.csv
```

Each file has:

```text
longitude,latitude
```

---

## Combined CLI usage

You can also run everything from the package CLI:

```bash
python -m crayfish_inertia task1
python -m crayfish_inertia task2
python -m crayfish_inertia task3
python -m crayfish_inertia all
```

---

## Locked endemic cohort

The initial cohort follows Lucian's email:

- Austropotamobius bihariensis
- Cambaroides similis
- Parastacus pugnax
- Cambarus eeseeohensis
- Cambarus reburrus
- Cambarus elkensis
- Cambarus lenati
- Cambarus hatfieldi

---

## Notes for Kristian

This is a packaging/export project, not a modeling project.

Before trusting the outputs, verify:

1. the input metrics are from `full_geofresh/GBM`;
2. the presence table contains the same thinned presences used for model fitting;
3. continental predictions are projected only to the species' continent of origin;
4. suitability scores are not compared directly across species without species-specific thresholding;
5. all exported coordinates are WGS84 longitude/latitude.
