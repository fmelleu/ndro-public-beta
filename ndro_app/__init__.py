"""NDRO Streamlit MVP application package.

This package contains all non-Streamlit-rendering logic (data loading,
validation, metrics, filters) as well as the Streamlit rendering helpers
(charts, cards, page views) for the NDRO public-snapshot MVP.

Nothing in this package connects to a database, calls a paid API, scrapes
PubMed, or requests credentials. It only reads local, versioned CSV/JSON
snapshot files described in
``contracts/NDRO_Public_Snapshot_Data_Contract_v0.1.md``.
"""

__all__ = []
