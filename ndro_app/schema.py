"""Column-level schema definitions drawn directly from
``contracts/NDRO_Public_Snapshot_Data_Contract_v0.1.md``.

Each list below is a literal transcription of the fields named in the
contract for that file. Keeping them here (instead of scattering column
name literals through the app) means a future contract patch only needs an
update in one place.
"""

# --- articles.csv --------------------------------------------------------
ARTICLES_IDENTITY_FIELDS = [
    "snapshot_version",
    "cutoff_date",
    "association_id",
    "disease_code",
    "pmid",
    "pubmed_url",
    "title",
    "publication_year",
    "journal",
]

ARTICLES_DISPLAY_FIELDS = [
    "authors",
    "abstract",
    "keywords",
    "publication_types",
]

ARTICLES_AUDIT_FIELDS = [
    "language_eligibility_status",
    "eligibility_status",
    "classification_status",
    "semantic_status",
    "relevance_class",
    "decision_code",
    "corpus_status",
    "final_label_source",
    "classification_version",
    "integrity_status",
    "integrity_last_checked_at",
    "plain_language_explanation",
    "eligibility_reason",
    "language_exclusion_reason",
    "association_updated_at",
]

ARTICLES_REQUIRED_COLUMNS = (
    ARTICLES_IDENTITY_FIELDS + ARTICLES_DISPLAY_FIELDS + ARTICLES_AUDIT_FIELDS
)

# Contract: "Required non-null values per row: snapshot_version, cutoff_date,
# association_id, disease_code, pmid, pubmed_url, title, publication_year,
# classification_status, semantic_status, integrity_status."
ARTICLES_REQUIRED_NONNULL = [
    "snapshot_version",
    "cutoff_date",
    "association_id",
    "disease_code",
    "pmid",
    "pubmed_url",
    "title",
    "publication_year",
    "classification_status",
    "semantic_status",
    "integrity_status",
]

# Numeric columns in articles.csv that should be parsed as numbers rather
# than left as text.
ARTICLES_NUMERIC_COLUMNS = ["publication_year"]

ARTICLES_PRIMARY_KEY = "association_id"

# --- coverage.csv ---------------------------------------------------------
COVERAGE_REQUIRED_COLUMNS = [
    "snapshot_version",
    "cutoff_date",
    "disease_code",
    "candidate_associations",
    "eligible_associations",
    "semantically_complete_associations",
    "semantic_coverage_percent",
    "core_associations",
    "separate_associations",
    "excluded_associations",
    "pending_final_classification",
    "last_updated_at",
]

COVERAGE_NUMERIC_COLUMNS = [
    "candidate_associations",
    "eligible_associations",
    "semantically_complete_associations",
    "semantic_coverage_percent",
    "core_associations",
    "separate_associations",
    "excluded_associations",
    "pending_final_classification",
]

# --- study_facts.csv -------------------------------------------------------
STUDY_FACTS_REQUIRED_COLUMNS = [
    "association_id",
    "disease_code",
    "corpus_status",
    "pmid",
    "publication_year",
    "publication_form",
    "population_description",
    "sample_size_total",
    "overall_treatment_signal",
    "extraction_confidence",
    "design_codes",
    "objective_codes",
    "context_codes",
    "methods",
    "models",
    "countries",
]

STUDY_FACTS_NUMERIC_COLUMNS = ["publication_year", "sample_size_total"]
STUDY_FACTS_PRIMARY_KEY = "association_id"

# --- evidence_spans.csv ----------------------------------------------------
EVIDENCE_SPANS_REQUIRED_COLUMNS = [
    "association_id",
    "disease_code",
    "pmid",
    "subject_type",
    "subject_id",
    "source_field",
    "evidence_text",
    "evidence_start",
    "evidence_end",
    "confidence",
]

EVIDENCE_SPANS_NUMERIC_COLUMNS = ["evidence_start", "evidence_end"]

# --- interventions_outcomes.csv -------------------------------------------
# The contract describes these fields narratively rather than as an exact
# column list. This is the column set actually shipped in the sample
# snapshot's header row, which we treat as the concrete contract for this
# file (see IMPLEMENTATION_DECISIONS.md).
INTERVENTIONS_OUTCOMES_REQUIRED_COLUMNS = [
    "association_id",
    "disease_code",
    "pmid",
    "corpus_status",
    "intervention_id",
    "intervention_name",
    "intervention_type",
    "therapeutic_intent",
    "dose",
    "route",
    "duration",
    "intervention_comparator",
    "intervention_confidence",
    "outcome_id",
    "outcome_name",
    "outcome_domain",
    "effect_direction",
    "reported_significance",
    "outcome_comparator",
    "result_summary",
    "outcome_confidence",
]

# Files that must contain exactly one row per association_id (the
# contract's stated grain for these two files).
FILES_REQUIRING_UNIQUE_ASSOCIATION_ID = ("articles.csv", "study_facts.csv")
