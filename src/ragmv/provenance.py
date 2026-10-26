"""Run identity helpers shared by the runners, the analyses and the artefact validator.

Runs written by the current runners (`ragmv.run`, `ragmv.run1b`) carry `schema = RUN_SCHEMA` and record a
configuration fingerprint, a content digest of the code and digests of the input files. The stored runs of
2026-10-18/19 predate that schema: their manifests describe the configuration, versions and platform but carry no
code or input digests, so their provenance is reported as incomplete rather than checked.
"""
from __future__ import annotations

RUN_SCHEMA = "ragmv.run/2"  # manifests written by ragmv.run / ragmv.run1b with adaptive-depth budget filling


def is_hex_digest(value, length: int = 64) -> bool:
    return isinstance(value, str) and len(value) == length and all(c in "0123456789abcdef" for c in value)
