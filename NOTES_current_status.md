# Current status — Endemism inertia project

Date: 2026-04-28

Lucian confirmed the final cohort is 7 species.

Dropped:
- Parastacus pugnax

Final cohort:
1. Austropotamobius bihariensis
2. Cambaroides similis
3. Cambarus eeseeohensis
4. Cambarus reburrus
5. Cambarus elkensis
6. Cambarus lenati
7. Cambarus hatfieldi

Task 1:
- Completed from Stage 3 full_geofresh/GBM outputs.
- Script: scripts/build_task1_from_stage3_outputs.py
- Local output: data/processed/task1_qc/endemic_cohort_data_check.csv

Task 3:
- Realized range exports can be generated from Stage 3 full_geofresh BIOMOD inputs.
- Script: scripts/build_task3_realized_exports_from_stage3.py
- Local outputs: data/processed/task3_realized/realized_{species_slug}.csv

Task 2:
- Draft script exists: scripts/build_task2_projection_exports_from_stage3.py
- Existing Stage 3 projections are matrix-target projections, not true full continental Hydrography90m projections.
- True Task 2 needs a continent-wide Hydrography90m / GeoFRESH environmental table for Europe, Asia, and North America.
