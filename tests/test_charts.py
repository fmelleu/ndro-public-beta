import pandas as pd

from ndro_app.charts import (
    candidate_landscape_chart,
    disease_trend_chart,
    publication_year_trend_chart,
)


def test_publication_year_chart_keeps_title_outside_the_altair_canvas():
    trend = pd.DataFrame({"publication_year": [2024, 2025], "count": [13, 9]})

    spec = publication_year_trend_chart(trend).to_dict()

    assert spec["height"] == 260
    assert "title" not in spec
    assert all("title" not in layer for layer in spec["layer"])


def test_candidate_landscape_uses_stable_horizontal_layout():
    landscape = pd.DataFrame(
        {
            "corpus_bucket": ["core", "separate", "excluded", "pending", "unrecognized"],
            "count": [151, 15, 239, 20, 0],
        }
    )

    spec = candidate_landscape_chart(landscape).to_dict()
    bar_encoding = spec["layer"][0]["encoding"]

    assert spec["height"] == 260
    assert "title" not in spec
    assert bar_encoding["x"]["field"] == "count"
    assert bar_encoding["x"]["stack"] is None
    assert bar_encoding["y"]["field"] == "label"
    assert bar_encoding["color"]["legend"] is None
    assert bar_encoding["y"]["sort"] == [
        "Core",
        "Separate view",
        "Excluded",
        "Pending",
        "Unrecognized",
    ]


def test_disease_trend_exposes_full_names_instead_of_codes():
    trend = pd.DataFrame(
        {
            "publication_year": [2024, 2024],
            "disease_code": ["AD", "PD"],
            "count": [13, 9],
        }
    )

    spec = disease_trend_chart(trend).to_dict()

    assert spec["encoding"]["color"]["field"] == "disease_name"
    assert "Alzheimer's disease" in spec["encoding"]["color"]["scale"]["domain"]
    assert "Parkinson's disease" in spec["encoding"]["color"]["scale"]["domain"]
