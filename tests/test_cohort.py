from crayfish_inertia.cohort import ENDEMIC_COHORT, cohort_species_names, species_to_file_stem


def test_cohort_has_eight_species():
    assert len(ENDEMIC_COHORT) == 8


def test_species_file_stem():
    assert species_to_file_stem("Austropotamobius bihariensis") == "Austropotamobius_bihariensis"


def test_species_names_are_unique():
    names = cohort_species_names()
    assert len(names) == len(set(names))
