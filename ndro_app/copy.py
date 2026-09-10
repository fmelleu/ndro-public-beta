"""Centralized scientific labels and copy.

Every user-facing string that describes NDRO status semantics, exclusions,
or evidence lives here, and only here, so the app never shows conflicting
explanations of the same concept in two different places. Wherever the
authoritative inputs give exact wording (the data contract or the UI
scientific requirements document), that wording is reproduced verbatim or
as close to verbatim as UI framing allows; nothing here is generated or
inferred by an LLM at runtime, and nothing here reads row-level data -- it
only describes what the fixed vocabulary of statuses means.
"""

APP_TITLE = "SynapSight — Neurodegenerative Disease Research Observatory"
APP_SUBTITLE = (
    "A living, auditable view of public PubMed evidence from versioned NDRO snapshots."
)

# Stable internal codes remain in the public data contract, but public-facing
# controls and charts use full names so non-specialist readers never need to
# decode an abbreviation. Unknown future codes are shown verbatim rather than
# assigned an invented name.
DISEASE_NAMES = {
    "AD": "Alzheimer's disease",
    "ALS": "Amyotrophic lateral sclerosis",
    "FTD": "Frontotemporal dementia",
    "HD": "Huntington's disease",
    "PD": "Parkinson's disease",
}


def disease_name(disease_code: object) -> str:
    """Return the public full name while preserving unknown codes."""
    code = str(disease_code or "").strip()
    return DISEASE_NAMES.get(code.upper(), code or "—")

PUBMED_DERIVED_RIGHTS_NOTICE = (
    "Titles, abstracts and other PubMed-derived fields are not relicensed by NDRO. "
    "They remain subject to the rights of their authors or publishers and to NLM "
    "terms. NLM notes that abstracts may be protected by copyright."
)
NLM_COPYRIGHT_INFORMATION_URL = "https://www.nlm.nih.gov/databases/download.html"

SYNTHETIC_DATA_BANNER = (
    "This preview is running against a **synthetic fixture snapshot**, "
    "built only to test this interface. It does not contain real NDRO or "
    "PubMed records, and nothing shown here should be read as a real "
    "research finding."
)

# --- Living-corpus status banner (Overview) -------------------------------
STATUS_BANNER = {
    "amber": {
        "label": "Amber — Classification in progress",
        "description": (
            "The system is operating, but some eligible records still lack "
            "complete semantic classification."
        ),
        "color": "#8a6100",
        "background": "#fff3cd",
        "icon": "●",  # filled circle; color + text label carries meaning, not color alone
    },
    "green": {
        "label": "Green — Snapshot complete",
        "description": (
            "Every eligible record in this named snapshot is semantically "
            "complete through its cutoff."
        ),
        "color": "#0f5132",
        "background": "#d1e7dd",
        "icon": "●",
    },
    "red": {
        "label": "Red — System or data failure",
        "description": "This snapshot reports an actual failed or invalid release.",
        "color": "#842029",
        "background": "#f8d7da",
        "icon": "●",
    },
}

STATUS_BANNER_UNKNOWN = {
    "label": "Status not recognized",
    "description": (
        "This snapshot's status_indicator value is not one of the three "
        "defined public statuses (amber/green/red). Treat this release "
        "with caution."
    ),
    "color": "#495057",
    "background": "#e2e3e5",
    "icon": "●",
}

LIVING_CORPUS_EXPLANATION = (
    "NDRO is a living corpus: new publication-disease associations are "
    "added over time and move through eligibility screening, relevance "
    "classification and semantic extraction at different speeds. A given "
    "snapshot is a frozen, versioned photograph of that process as of its "
    "cutoff date -- later snapshots may reclassify or complete records that "
    "are still pending here."
)

# --- Public-facing project rationale (Overview) ---------------------------
# The numerical statements below are intentionally limited to the scope
# supported by the linked GBD/WHO sources. Mental-disorder estimates are not
# added to the neurological denominator, and NDRO's narrower
# neurodegenerative scope remains explicit.
PURPOSE_TEXT = (
    "Neurological conditions are the leading cause of ill health and "
    "disability worldwide. The Global Burden of Disease 2021 analysis "
    "estimated that 3.4 billion people—43.1% of the global population—were "
    "living with a neurological condition in 2021, while the associated "
    "disability-adjusted life years increased by approximately 18% from 1990. "
    "Dementia is among the major contributors to this burden, and "
    "neurodegenerative diseases have growing consequences for individuals, "
    "families, health systems and economies.\n\n"
    "The scale and heterogeneity of this evidence make transparent, "
    "continuously updated research infrastructure essential. NDRO organizes "
    "public PubMed evidence on neurodegenerative diseases into a versioned, "
    "auditable corpus: preserving source records, making eligibility and "
    "relevance decisions inspectable, and distinguishing candidate, "
    "analytical and semantically completed evidence. This purpose supports "
    "the WHO call to strengthen neurological research and data systems and "
    "aligns with UN Sustainable Development Goal 3, particularly Targets 3.4 "
    "and 3.b."
)

PURPOSE_SOURCES = (
    "Scientific basis: [GBD 2021 neurological burden — WHO summary]"
    "(https://www.who.int/news/item/14-03-2024-over-1-in-3-people-affected-by-neurological-conditions--the-leading-cause-of-illness-and-disability-worldwide)"
    " · [WHO Intersectoral Global Action Plan on neurological disorders]"
    "(https://www.who.int/publications/i/item/9789240076624)"
    " · [UN Sustainable Development Goal 3]"
    "(https://sdgs.un.org/goals/goal3)"
)

MISSION_TEXT = (
    "Make the public evidence landscape for neurodegenerative diseases easier "
    "to inspect, reproduce and improve. NDRO connects aggregate indicators to "
    "their publication–disease associations, documents exclusions and "
    "uncertainty, and invites traceable community corrections without changing "
    "canonical classifications automatically."
)

HOW_TO_USE_STEPS = (
    "1. **Orient yourself:** use Overview to confirm the snapshot, cutoff, "
    "release status and denominators.\n"
    "2. **Explore the evidence:** search Article Explorer and compare disease "
    "and geographic views.\n"
    "3. **Audit decisions:** inspect inclusion or exclusion reasons and report a "
    "possible error through the prefilled audit form.\n"
    "4. **Cite precisely:** record the snapshot version and cutoff date whenever "
    "you reuse or discuss an NDRO result."
)

# --- Planned updates -------------------------------------------------------
ROADMAP_INTRO = (
    "NDRO is being developed in versioned stages. This roadmap records the "
    "planned order of work, not fixed delivery dates. A feature moves into a "
    "public release only after its data source, validation rules and scientific "
    "limitations are documented. Streamlit and Power BI will continue to be "
    "released together from the same immutable public snapshot."
)

ROADMAP_PHASES = (
    {
        "phase": "1",
        "title": "Public-beta infrastructure",
        "status": "Current priority",
        "description": (
            "Deploy the first synchronized Streamlit and read-only Power BI beta; "
            "establish PostgreSQL staging, backups, immutable public snapshots, "
            "automated validation and a complete test update from extraction to publication."
        ),
    },
    {
        "phase": "2",
        "title": "Validated semantic layer",
        "status": "Next scientific milestone",
        "description": (
            "Benchmark local language models against a human-reviewed gold set and "
            "extract study design, experimental model, species or cell system, "
            "mechanisms, interventions and outcomes. Every extracted claim must keep "
            "a literal evidence span, confidence, model version and review status."
        ),
    },
    {
        "phase": "3",
        "title": "Research landscape enrichment",
        "status": "Planned",
        "description": (
            "Add author and responsible-institution geography, citation indicators "
            "and citation networks, and research-funding information by disease, "
            "country, institution and funder. Funding acknowledgements, grant awards "
            "and national investment indicators will remain distinct."
        ),
    },
    {
        "phase": "4",
        "title": "Evidence-gap analysis",
        "status": "Planned",
        "description": (
            "Identify underrepresented models, mechanisms, interventions, diseases, "
            "geographies and funding patterns. Low volume will be presented as a "
            "potential evidence gap, not as proof that a topic has been neglected."
        ),
    },
    {
        "phase": "5",
        "title": "Corpus expansion",
        "status": "After the update pipeline is stable",
        "description": (
            "Introduce additional diseases through the same documented search, review "
            "and validation protocol. Multiple sclerosis is the final currently planned "
            "expansion and will include an explicit scope note distinguishing its "
            "immune-mediated demyelinating biology from its neurodegenerative components."
        ),
    },
)

# --- Review protocol -------------------------------------------------------
PROTOCOL_VERSION = "NDRO review protocol v0.1"

SEARCH_QUERIES = (
    {
        "disease": "Alzheimer's disease",
        "query": '"Alzheimer Disease"[MeSH Terms] OR Alzheimer*[Title/Abstract]',
    },
    {
        "disease": "Amyotrophic lateral sclerosis",
        "query": (
            '"Amyotrophic Lateral Sclerosis"[MeSH Terms] OR '
            '"amyotrophic lateral sclerosis"[Title/Abstract]'
        ),
    },
    {
        "disease": "Frontotemporal dementia",
        "query": (
            '"Frontotemporal Dementia"[MeSH Terms] OR '
            '"Frontotemporal Lobar Degeneration"[MeSH Terms] OR '
            'frontotemporal*[Title/Abstract]'
        ),
    },
    {
        "disease": "Huntington's disease",
        "query": '"Huntington Disease"[MeSH Terms] OR Huntington*[Title/Abstract]',
    },
    {
        "disease": "Parkinson's disease",
        "query": '"Parkinson Disease"[MeSH Terms] OR Parkinson*[Title/Abstract]',
    },
)

SEARCH_PROTOCOL_NOTE = (
    "These are the current candidate-query strings recorded in NDRO ingestion "
    "artifacts. Every retrieval run adds its exact date window and PubMed date "
    "field to a versioned run manifest. The query retrieves candidates; it does "
    "not by itself establish inclusion in the analytical corpus."
)

DEDUPLICATION_NOTE = (
    "NDRO stores a publication once by PMID and represents each disease match as "
    "a separate publication–disease association. Repeated retrieval of the same "
    "PMID for the same disease is collapsed deterministically. A PMID associated "
    "with more than one disease is retained in each relevant disease association; "
    "it is not treated as an accidental duplicate. Source XML remains preserved."
)

DETERMINISTIC_RULES = (
    ("E_ABS_01", "Exclude from analytical eligibility when the PubMed abstract is missing."),
    ("E_ABS_02", "Exclude when the available PubMed abstract is explicitly truncated."),
    (
        "E_LANG_01",
        "Exclude when no adequate English scientific abstract is available; an English plain-language summary alone is insufficient.",
    ),
    (
        "E_DESIGN_01",
        "Exclude reviews, systematic reviews, meta-analyses, case reports or series, editorials, letters, comments and protocols without original results.",
    ),
    (
        "I1",
        "Pass to relevance screening when the record is original empirical research with an adequate English scientific abstract.",
    ),
)

RELEVANCE_ROUTING = (
    ("Primary focus / co-primary focus", "Core analytical corpus"),
    ("Shared mechanism or secondary disease context", "Separate analytical view"),
    ("Background mention / comparative mention / not relevant", "Relevance exclusion"),
    ("Uncertain", "Human adjudication before final placement"),
)

PROTOCOL_FLOW_HTML = """
<div class="ndro-protocol-flow" role="img" aria-label="NDRO review protocol flowchart">
  <div class="flow-stage flow-source"><b>1 · Versioned search protocol</b><span>Disease query, date window, PubMed date field and run identifier</span></div>
  <div class="flow-arrow">↓</div>
  <div class="flow-stage"><b>2 · PubMed ESearch</b><span>Retrieve candidate PMIDs; partition result sets above 10,000 by publication date</span></div>
  <div class="flow-arrow">↓</div>
  <div class="flow-stage"><b>3 · PubMed EFetch</b><span>Download complete PubMed XML and preserve the raw response before flattening</span></div>
  <div class="flow-arrow">↓</div>
  <div class="flow-stage"><b>4 · Parse, normalize and reconcile</b><span>Journal and Bookshelf records, dates, abstract variants, publication types, relations and source hashes</span></div>
  <div class="flow-arrow">↓</div>
  <div class="flow-stage"><b>5 · PMID-aware duplicate handling</b><span>One publication record; one auditable association for every matched disease</span></div>
  <div class="flow-arrow">↓</div>
  <div class="flow-stage flow-decision"><b>6 · Deterministic eligibility screen</b><span>Abstract provenance and completeness, English scientific abstract, original empirical publication form</span></div>
  <div class="flow-branches">
    <div>
      <div class="flow-branch-label">Eligible</div><div class="flow-arrow">↓</div>
      <div class="flow-stage flow-future"><b>7 · Relevance screen</b><span>Pilot classifications exist; the validated production semantic worker is planned</span></div>
      <div class="flow-route-grid">
        <div><div class="flow-branch-label">Core / separate</div><div class="flow-arrow">↓</div><div class="flow-stage flow-future"><b>8 · Deep semantic extraction — planned</b><span>Study design, models, mechanisms, interventions and outcomes with literal evidence spans</span></div></div>
        <div><div class="flow-branch-label">Not relevant</div><div class="flow-arrow">↓</div><div class="flow-stage flow-exclusion"><b>Relevance exclusion</b><span>Scientific reason retained; no unnecessary deep extraction</span></div></div>
      </div>
    </div>
    <div><div class="flow-branch-label">Ineligible</div><div class="flow-arrow">↓</div><div class="flow-stage flow-exclusion"><b>Eligibility exclusion</b><span>Reason and rule are retained; the record remains searchable and auditable</span></div></div>
  </div>
  <div class="flow-arrow">↓</div>
  <div class="flow-stage"><b>9 · Canonical PostgreSQL</b><span>Raw/source, canonical, semantic and audit history remain separate; accepted changes create revisions</span></div>
  <div class="flow-arrow">↓</div>
  <div class="flow-stage"><b>10 · Frozen public snapshot</b><span>CSV/JSON export, privacy minimization, contract validation, checksums, version and cutoff</span></div>
  <div class="flow-arrow">↓</div>
  <div class="flow-stage flow-output"><b>11 · Synchronized presentation</b><span>Interactive Streamlit for scientific inspection and audit · read-only Power BI for public indicators</span></div>
  <div class="flow-loop">Community report → curator review → accepted revision → later versioned snapshot. No submission edits the live snapshot automatically.</div>
</div>
"""

PROTOCOL_STATUS_NOTE = (
    "Solid stages are implemented in the current NDRO architecture or release "
    "tooling. Dashed green stages describe the intended production semantic "
    "workflow. The current snapshot contains pilot semantic classifications, but "
    "the full-scale automated semantic layer is not yet in production."
)

RETRACTION_PROTOCOL = (
    "NDRO does not erase a source record because it is retracted. PubMed integrity "
    "relations are checked and stored. A confirmed retraction is excluded from "
    "analytical indicators by default, while the publication, warning, prior "
    "classification and audit history remain inspectable. Corrections and expressions "
    "of concern are displayed as integrity signals and reviewed according to their status."
)

# --- Corpus status (per-association) --------------------------------------
CORPUS_BUCKET_LABELS = {
    "core": "Core analytical corpus",
    "separate": "Separate analytical view",
    "excluded": "Excluded from the corpus",
    "pending": "Pending — not yet placed",
    "unrecognized": "Unrecognized status (flagged for review)",
}

CORPUS_BUCKET_SHORT_BADGE = {
    "core": "Core",
    "separate": "Separate view",
    "excluded": "Excluded",
    "pending": "Pending",
    "unrecognized": "Unrecognized",
}

CORPUS_BUCKET_COLORS = {
    # Chosen for readable contrast against a light background in both the
    # badge text and the badge fill; color is always paired with a text
    # label (never color alone) per the accessibility requirement.
    "core": {"fg": "#0f5132", "bg": "#d1e7dd"},
    "separate": {"fg": "#084298", "bg": "#cfe2ff"},
    "excluded": {"fg": "#842029", "bg": "#f8d7da"},
    "pending": {"fg": "#664d03", "bg": "#fff3cd"},
    "unrecognized": {"fg": "#41464b", "bg": "#e2e3e5"},
}

CORPUS_BUCKET_EXPLANATION = {
    "core": (
        "This association is part of NDRO's core analytical corpus: its "
        "disease relationship is the primary focus of the publication and "
        "it has passed eligibility and relevance classification. Semantic "
        "extraction completeness is reported separately."
    ),
    "separate": (
        "This association is preserved in a separate analytical view. "
        "'Separate' is preserved evidence, not rejection, and it is not "
        "part of the core analytical indicators."
    ),
    "excluded": (
        "This association did not meet NDRO's eligibility or scientific "
        "relevance criteria and is excluded from the corpus. Exclusion is "
        "a scientific/eligibility decision, not a data-quality problem."
    ),
    "pending": (
        "This association has not yet received a final NDRO classification. "
        "Pending is not the same as excluded -- it simply has not been "
        "placed yet."
    ),
    "unrecognized": (
        "This record's corpus_status value is not one of the statuses this "
        "app build recognizes. It is shown for transparency but excluded "
        "from every headline count until reviewed."
    ),
}

# Row-level exclusion criteria. These labels translate only the controlled
# values already stored in the snapshot; they do not infer a reason from the
# title or abstract.
ELIGIBILITY_EXCLUSION_CRITERIA = {
    "revisão ou meta-análise": "Review or meta-analysis",
    "abstract ausente": "Missing abstract",
    "abstract_missing": "Missing abstract",
    "relato ou série de casos": "Case report or case series",
    "texto narrativo sem dados empíricos originais": (
        "Narrative text without original empirical data"
    ),
    "revisão narrativa sem dados empíricos originais": (
        "Narrative review without original empirical data"
    ),
    "editorial, comentário ou carta": "Editorial, commentary, or letter",
    "not_original_empirical_research": "Not original empirical research",
    "review article; no original empirical study.": (
        "Review article without an original empirical study"
    ),
    "historical and sociocultural article without an original empirical study.": (
        "Historical or sociocultural article without an original empirical study"
    ),
    "registry establishment report describing future data collection without empirical participant results.": (
        "Registry report describing planned data collection without empirical participant results"
    ),
}

RELEVANCE_EXCLUSION_CRITERIA = {
    "background_mention": "Target disease appears only as background context",
    "not_relevant": "Not relevant to the target disease",
    "comparative_mention": "Target disease is mentioned only for comparison",
}


def plain_language_question(bucket: str) -> str:
    """Return the exact fixed question for the collapsed selection panel,
    per the UI scientific requirements. Never invent a new question."""
    return {
        "core": "Why was this article included?",
        "separate": "Why is this article in a separate view?",
        "excluded": "Why was this article excluded from the corpus?",
        "pending": "Why is this article not included in the current analysis?",
        "unrecognized": "Why is this article not included in the current analysis?",
    }.get(bucket, "Why is this article not included in the current analysis?")


# --- Classification / semantic / integrity status legend ------------------
CLASSIFICATION_STATUS_LABELS = {
    "final": "Final",
    "semantic_pending": "Semantic classification pending",
}

SEMANTIC_STATUS_LABELS = {
    "complete": "Semantically complete",
    "pending": "Semantic extraction pending",
    "not_applicable": "Not applicable (excluded before semantic extraction)",
}

INTEGRITY_CLEAN_EXPLANATION = (
    "'no_pubmed_integrity_signal' does not prove that a publication has no "
    "problem. It only reports that the most recent supported PubMed "
    "integrity check found no retraction or correction signal at that time."
)

INTEGRITY_FLAGGED_EXPLANATION = (
    "The last PubMed integrity check may report a retraction, correction or "
    "another integrity signal. Confirmed retractions are excluded from core "
    "analytical indicators. Corrections remain visible and analytical unless "
    "a separate scientific decision changes their corpus placement."
)

# --- Evidence span headings ------------------------------------------------
# subject_type is the raw stored field. This maps it to a friendlier
# heading for the plain-language panel, per the UI scientific requirements'
# example heading set. No text here changes the meaning of the stored span
# -- it only relabels the existing subject_type for readability.
EVIDENCE_HEADING_MAP = {
    "study_context": "Human / animal / in vitro context",
    "population": "Population studied",
    "study_objective": "Study objective / mechanism",
    "disease_focus": "Disease focus",
    "intervention": "Intervention",
    "outcome": "Outcome",
    "result_direction": "Result direction",
}


def evidence_heading(subject_type: str) -> str:
    if subject_type in EVIDENCE_HEADING_MAP:
        return EVIDENCE_HEADING_MAP[subject_type]
    # Fall back to a readable version of the raw value rather than
    # inventing an unrelated heading.
    return str(subject_type).replace("_", " ").strip().capitalize()


# --- Community invitation (read-only) --------------------------------------
COMMUNITY_INVITATION_TEXT = "Do you think this classification is wrong? Help us improve the NDRO corpus."
COMMUNITY_INVITATION_DISABLED_NOTE = "Opens the NDRO audit form with this record prefilled."
AUDIT_CONTACT_EMAIL = "ndro.project@proton.me"

AUDIT_SCIENTIFIC_GUARDRAIL = (
    "Community reports are audit candidates, not automatic corrections. "
    "They never modify the displayed snapshot or the canonical NDRO database. "
    "An accepted correction is applied by the NDRO review process and appears "
    "only in a later versioned snapshot."
)

AUDIT_PRIVACY_NOTICE = (
    "NDRO uses your name, email address and ORCID only to review this report, "
    "contact you if clarification is needed, and send one closing message with "
    "the outcome and our thanks. These identifiers are temporarily processed "
    "through Formspree and the NDRO Proton Mail inbox. After the audit decision "
    "and closing message, NDRO will delete the identifiable submission from its "
    "operational accounts. Your identity will not be published, sold, used for "
    "marketing or profiling, or linked to the public correction history. NDRO "
    "retains only the corrected scientific record, its non-personal version "
    "history, and aggregate counts of community corrections. Do not submit "
    "sensitive personal or health information. Privacy or deletion requests: "
    f"[{AUDIT_CONTACT_EMAIL}](mailto:{AUDIT_CONTACT_EMAIL})."
)

AUDIT_CONSENT_LABEL = (
    "I consent to NDRO processing my name, email address and ORCID only to "
    "review this audit report, contact me if clarification is required, and "
    "send one closing message."
)

AUDIT_PRIVACY_NOTICE_VERSION = "2026-09-03"

# --- Methods & Data Quality page ------------------------------------------
EVIDENCE_BOUNDARY_TEXT = (
    "NDRO builds this snapshot from public PubMed metadata and adequate "
    "English-language scientific abstracts. It does not routinely assess "
    "full text, and any conclusion here is bounded by what is present in "
    "the title, abstract, and structured metadata PubMed publishes."
)

EXCLUSIONS_EXPLANATION = (
    "Records are excluded from the core/separate corpus for one of two "
    "documented reasons: an eligibility exclusion (for example, a case "
    "report rather than an original cohort study, or a non-English-only "
    "abstract) or a relevance exclusion (the named disease is only a "
    "background mention rather than the study's focus). Exclusion reflects "
    "a scientific or eligibility judgment recorded at the time of "
    "classification -- it is not a data error, and excluded records remain "
    "visible and searchable in the Article Explorer."
)

NON_ENGLISH_EXPLANATION = (
    "Non-English-only scientific abstracts are excluded upstream of this "
    "application rather than translated by the UI."
)

INTERVENTIONS_OUTCOMES_DISCLAIMER = (
    "Intervention and outcome fields are descriptive, abstract-level "
    "extractions of what a publication reported. MVP v0.1 does not present "
    "them as a causal or clinical-effectiveness estimate."
)

DENOMINATOR_DISCLOSURE = (
    "Candidate, core-analytical and semantically-complete counts are "
    "different denominators and are never combined into a single number "
    "without saying which one is being shown."
)

# --- Geographic coverage --------------------------------------------------
GEOGRAPHIC_SCOPE_NOTICE = (
    "Countries are extracted from study descriptions in PubMed metadata for "
    "completed semantic records. They may represent study populations or "
    "scientific contexts; they are not author-affiliation countries."
)

GEOGRAPHIC_FUTURE_SCOPE = (
    "This snapshot contains only the study-context country dimension. "
    "Future releases will add author-affiliation country and responsible "
    "institution as separate variables."
)
