"""Locked endemic crayfish cohort for the ecological inertia project."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EndemicSpecies:
    species: str
    continent: str
    note: str

    @property
    def file_stem(self) -> str:
        """Filesystem-safe species name."""
        return self.species.replace(" ", "_")


ENDEMIC_COHORT: tuple[EndemicSpecies, ...] = (
    EndemicSpecies(
        species="Austropotamobius bihariensis",
        continent="Europe",
        note="Apuseni Mountains, Romania",
    ),
    EndemicSpecies(
        species="Cambaroides similis",
        continent="Asia",
        note="Korean Peninsula",
    ),
    EndemicSpecies(
        species="Parastacus pugnax",
        continent="South America",
        note="Central Chile",
    ),
    EndemicSpecies(
        species="Cambarus eeseeohensis",
        continent="North America",
        note="Appalachian / Cumberland Plateau",
    ),
    EndemicSpecies(
        species="Cambarus reburrus",
        continent="North America",
        note="Appalachian / Cumberland Plateau",
    ),
    EndemicSpecies(
        species="Cambarus elkensis",
        continent="North America",
        note="Appalachian / Cumberland Plateau",
    ),
    EndemicSpecies(
        species="Cambarus lenati",
        continent="North America",
        note="Appalachian / Cumberland Plateau",
    ),
    EndemicSpecies(
        species="Cambarus hatfieldi",
        continent="North America",
        note="Appalachian / Cumberland Plateau",
    ),
)


def cohort_species_names() -> list[str]:
    return [item.species for item in ENDEMIC_COHORT]


def species_to_file_stem(species: str) -> str:
    return species.replace(" ", "_")
