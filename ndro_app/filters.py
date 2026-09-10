"""Search, filtering and pagination for the Article Explorer.

All functions here are plain pandas and take/return DataFrames -- no
Streamlit calls -- so they can be unit tested directly and reused by any
future page.
"""

from __future__ import annotations

from typing import Iterable, Optional, Tuple

import pandas as pd

SEARCH_COLUMNS = ["pmid", "title", "authors", "abstract", "keywords"]


def search_articles(df: pd.DataFrame, query: Optional[str]) -> pd.DataFrame:
    """Case-insensitive substring search across PMID, title, authors,
    abstract and keywords, per the UI scientific requirements.

    A blank/None query returns the frame unchanged. Null field values are
    treated as empty strings rather than raising or matching everything.
    """
    if query is None or str(query).strip() == "":
        return df
    needle = str(query).strip().lower()
    mask = pd.Series(False, index=df.index)
    for col in SEARCH_COLUMNS:
        if col not in df.columns:
            continue
        haystack = df[col].fillna("").astype(str).str.lower()
        mask = mask | haystack.str.contains(needle, regex=False, na=False)
    return df[mask]


def apply_filters(
    df: pd.DataFrame,
    disease_codes: Optional[Iterable[str]] = None,
    year_range: Optional[Tuple[int, int]] = None,
    corpus_buckets: Optional[Iterable[str]] = None,
    classification_statuses: Optional[Iterable[str]] = None,
    semantic_statuses: Optional[Iterable[str]] = None,
    integrity_states: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """Apply the Article Explorer's filter set. Every argument is optional;
    an empty/None filter leaves that dimension unfiltered rather than
    excluding every row (an empty multiselect means "no restriction", to
    avoid the common UX trap of an empty filter silently hiding everything).
    """
    out = df

    if disease_codes:
        out = out[out["disease_code"].isin(list(disease_codes))]

    if year_range and "publication_year" in out.columns:
        lo, hi = year_range
        years = pd.to_numeric(out["publication_year"], errors="coerce")
        # NaN years compare False in .between(), so rows with an unknown
        # year are excluded from a year-restricted view rather than raising.
        out = out[years.between(lo, hi, inclusive="both")]

    if corpus_buckets and "corpus_bucket" in out.columns:
        out = out[out["corpus_bucket"].isin(list(corpus_buckets))]

    if classification_statuses and "classification_status" in out.columns:
        out = out[out["classification_status"].fillna("").isin(list(classification_statuses))]

    if semantic_statuses and "semantic_status" in out.columns:
        out = out[out["semantic_status"].fillna("").isin(list(semantic_statuses))]

    if integrity_states and "integrity_status" in out.columns:
        out = out[out["integrity_status"].fillna("").isin(list(integrity_states))]

    return out


def paginate(df: pd.DataFrame, page: int, page_size: int) -> Tuple[pd.DataFrame, int]:
    """Return (page_slice, total_pages). ``page`` is 1-indexed. Bounds are
    clamped so an out-of-range page never raises or returns an incoherent
    slice; an empty frame yields one (empty) page rather than zero pages so
    callers can always render a "page X of Y" control safely.
    """
    total_rows = len(df)
    total_pages = max(1, -(-total_rows // page_size)) if page_size > 0 else 1
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    return df.iloc[start:end], total_pages
