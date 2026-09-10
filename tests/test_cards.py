import pandas as pd

from ndro_app import copy
from ndro_app.cards import _abstract_source_notice, _badge_html, exclusion_reason_details


def test_disease_codes_have_plain_language_public_names():
    assert copy.disease_name("AD") == "Alzheimer's disease"
    assert copy.disease_name("ALS") == "Amyotrophic lateral sclerosis"
    assert copy.disease_name("FTD") == "Frontotemporal dementia"
    assert copy.disease_name("HD") == "Huntington's disease"
    assert copy.disease_name("PD") == "Parkinson's disease"
    assert copy.disease_name("NEW") == "NEW"


def test_badge_html_escapes_snapshot_derived_text():
    rendered = _badge_html('<img src=x onerror="alert(1)">', "#000", "#fff")

    assert "<img" not in rendered
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;" in rendered


def test_abstract_notice_names_pubmed_rights_and_links_to_source_and_nlm():
    notice = _abstract_source_notice("https://pubmed.ncbi.nlm.nih.gov/123456/")

    assert "From PubMed metadata" in notice
    assert "not relicensed by NDRO" in notice
    assert "https://pubmed.ncbi.nlm.nih.gov/123456/" in notice
    assert "https://www.nlm.nih.gov/databases/download.html" in notice


def test_eligibility_exclusion_shows_the_recorded_criterion():
    row = pd.Series(
        {
            "corpus_status": "excluded_eligibility",
            "eligibility_reason": "Revisão ou meta-análise",
            "language_exclusion_reason": "",
        }
    )

    assert exclusion_reason_details(row) == {
        "layer": "Eligibility",
        "criterion": "Review or meta-analysis",
    }


def test_relevance_exclusion_uses_relevance_class_not_eligibility_reason():
    row = pd.Series(
        {
            "corpus_status": "excluded_relevance",
            "eligibility_reason": "Estudo empírico original com abstract utilizável",
            "relevance_class": "background_mention",
        }
    )

    assert exclusion_reason_details(row) == {
        "layer": "Relevance",
        "criterion": "Target disease appears only as background context",
    }


def test_eligibility_exclusion_preserves_an_additional_language_note():
    row = pd.Series(
        {
            "corpus_status": "excluded_eligibility",
            "eligibility_reason": "Abstract ausente",
            "language_exclusion_reason": "Abstract missing from the public PubMed record.",
        }
    )

    assert exclusion_reason_details(row) == {
        "layer": "Eligibility",
        "criterion": "Missing abstract",
        "additional_note": "Abstract missing from the public PubMed record.",
    }
