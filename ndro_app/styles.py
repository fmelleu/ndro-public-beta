"""Shared visual styling for the public beta interface.

The CSS stays deliberately modest: it improves hierarchy, wrapping and
responsive behaviour without changing Streamlit's interaction model or the
scientific content of any page.
"""

GLOBAL_STYLES = """
<style>
  :root {
    --ndro-green: #2f6f4f;
    --ndro-green-dark: #24563e;
    --ndro-border: #dfe7e2;
    --ndro-muted: #5f6b64;
    --ndro-surface: #f7f9f8;
  }

  .block-container {
    max-width: 1180px;
    padding-top: 1.2rem;
    padding-bottom: 2.5rem;
  }

  h1 {
    font-size: clamp(1.9rem, 3.2vw, 2.65rem) !important;
    line-height: 1.12 !important;
    letter-spacing: -0.025em;
  }

  h2, h3 {
    letter-spacing: -0.015em;
  }

  [data-testid="stCaptionContainer"] {
    color: var(--ndro-muted);
    line-height: 1.45;
  }

  [data-testid="stMetric"] {
    min-height: 104px;
    padding: 0.9rem 1rem 0.8rem;
    background: #ffffff;
    border: 1px solid var(--ndro-border);
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(24, 51, 38, 0.04);
  }

  [data-testid="stMetricLabel"] p {
    white-space: normal;
    line-height: 1.25;
  }

  [data-testid="stMetricValue"] {
    font-size: clamp(1.45rem, 2.4vw, 2rem);
    line-height: 1.15;
  }

  [data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--ndro-border);
    border-radius: 12px;
  }

  [data-testid="stDataFrame"] {
    overflow: hidden;
    border: 1px solid var(--ndro-border);
    border-radius: 10px;
  }

  .stButton > button,
  .stDownloadButton > button,
  .stLinkButton > a {
    border-radius: 8px;
  }

  .ndro-info-card {
    height: 100%;
    min-height: 92px;
    padding: 0.85rem 1rem;
    background: #ffffff;
    border: 1px solid var(--ndro-border);
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(24, 51, 38, 0.04);
  }

  .ndro-info-label {
    margin-bottom: 0.25rem;
    color: var(--ndro-muted);
    font-size: 0.8rem;
    line-height: 1.2;
  }

  .ndro-info-value {
    color: #1c1f1e;
    font-size: 1.02rem;
    font-weight: 650;
    line-height: 1.28;
    overflow-wrap: anywhere;
  }

  .ndro-protocol-flow {
    max-width: 920px;
    margin: 0.5rem auto 1rem;
  }

  .flow-stage {
    display: flex;
    flex-direction: column;
    gap: 0.28rem;
    padding: 0.8rem 1rem;
    color: #24312a;
    background: #ffffff;
    border: 1px solid var(--ndro-border);
    border-left: 5px solid #6c8b7a;
    border-radius: 10px;
    box-shadow: 0 1px 2px rgba(24, 51, 38, 0.05);
    text-align: left;
  }

  .flow-stage b {
    color: var(--ndro-green-dark);
    font-size: 1rem;
  }

  .flow-stage span,
  .flow-loop {
    font-size: 0.88rem;
    line-height: 1.4;
  }

  .flow-source,
  .flow-output {
    background: #edf6f1;
    border-left-color: var(--ndro-green);
  }

  .flow-decision {
    background: #f3f6f4;
    border-left-color: #4f6f5e;
  }

  .flow-future {
    background: #f4faf7;
    border: 2px dashed #76a48c;
  }

  .flow-exclusion {
    background: #fff8f6;
    border-left-color: #a45d4f;
  }

  .flow-arrow {
    padding: 0.12rem 0;
    color: #6c7c73;
    font-size: 1.25rem;
    font-weight: 700;
    line-height: 1;
    text-align: center;
  }

  .flow-branches {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 1rem;
  }

  .flow-route-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
    gap: 0.65rem;
  }

  .flow-branch-label {
    margin-top: 0.35rem;
    color: var(--ndro-muted);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-align: center;
    text-transform: uppercase;
  }

  .flow-loop {
    margin-top: 0.9rem;
    padding: 0.7rem 0.9rem;
    color: #584814;
    background: #fff8dc;
    border: 1px solid #eadb9a;
    border-radius: 9px;
  }

  @media (max-width: 768px) {
    .block-container {
      padding: 0.85rem 1rem 2rem;
    }

    h1 {
      font-size: 1.75rem !important;
    }

    [data-testid="stMetric"],
    .ndro-info-card {
      min-height: auto;
    }

    .flow-branches {
      grid-template-columns: 1fr;
    }

    .flow-route-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
"""
