"""Small, reusable presentation helpers."""

from __future__ import annotations

import html


def info_card(container, label: str, value: object, help_text: str = "") -> None:
    """Render a compact card whose value wraps instead of truncating."""
    title = f' title="{html.escape(help_text)}"' if help_text else ""
    container.markdown(
        '<div class="ndro-info-card">'
        f'<div class="ndro-info-label">{html.escape(str(label))}</div>'
        f'<div class="ndro-info-value"{title}>{html.escape(str(value))}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
