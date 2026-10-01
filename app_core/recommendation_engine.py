"""Generate clear privacy recommendations from a scan result."""


def generate_recommendations(
    risk_level: str, pii_types: set[str], encryption_status: str
) -> list[dict[str, str]]:
    """Return non-sensitive, actionable recommendations for a document."""
    recommendations: list[dict[str, str]] = []

    if encryption_status != "encrypted":
        recommendations.append(
            {
                "recommendation_text": "Encrypt this document before storing or sharing it.",
                "priority": "high",
            }
        )

    if risk_level in {"high", "critical"}:
        recommendations.append(
            {
                "recommendation_text": "Restrict document access to only users with a clear need to view it.",
                "priority": "high",
            }
        )
    elif risk_level == "medium":
        recommendations.append(
            {
                "recommendation_text": "Review the document before sharing and remove unnecessary personal information.",
                "priority": "medium",
            }
        )
    else:
        recommendations.append(
            {
                "recommendation_text": "Keep access limited and rescan this document after any future edits.",
                "priority": "low",
            }
        )

    if {"aadhaar", "pan", "payment_card"} & pii_types:
        recommendations.append(
            {
                "recommendation_text": "Mask or remove identity and financial identifiers before external sharing.",
                "priority": "high",
            }
        )
    elif {"email", "phone"} & pii_types:
        recommendations.append(
            {
                "recommendation_text": "Avoid publishing contact details unless they are required for the document's purpose.",
                "priority": "medium",
            }
        )

    return recommendations
