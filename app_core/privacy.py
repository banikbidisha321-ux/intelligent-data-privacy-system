"""Local, rule-based PII detection and privacy-risk calculation."""

import re


PII_WEIGHTS = {
    "email": 10,
    "phone": 20,
    "aadhaar": 40,
    "pan": 35,
    "payment_card": 50,
}

PATTERNS = (
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    (
        "payment_card",
        re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)"),
    ),
    ("aadhaar", re.compile(r"(?<!\d)[2-9]\d{3}[-\s]?\d{4}[-\s]?\d{4}(?!\d)")),
    ("pan", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")),
    ("phone", re.compile(r"(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)")),
)


def _is_luhn_valid(value: str) -> bool:
    """Check a potential payment-card number without retaining its value."""
    digits = "".join(character for character in value if character.isdigit())
    if not 13 <= len(digits) <= 19:
        return False

    checksum = 0
    for index, digit in enumerate(reversed(digits)):
        number = int(digit)
        if index % 2 == 1:
            number *= 2
            if number > 9:
                number -= 9
        checksum += number
    return checksum % 10 == 0


def redact(value: str) -> str:
    """Return a masked representation; never persist the original PII value."""
    if "@" in value:
        local_part, domain = value.split("@", 1)
        return f"{local_part[:1]}***@{domain}"

    visible_suffix = "".join(character for character in value if character.isalnum())[-4:]
    return f"XXXX-XXXX-{visible_suffix}"


def detect_pii(text: str) -> list[dict[str, object]]:
    """Find supported PII types and return only redacted, in-memory results."""
    findings = []
    occupied_spans: list[tuple[int, int]] = []
    seen = set()

    for pii_type, pattern in PATTERNS:
        for match in pattern.finditer(text):
            if any(match.start() < end and match.end() > start for start, end in occupied_spans):
                continue

            raw_value = match.group(0)
            if pii_type == "payment_card" and not _is_luhn_valid(raw_value):
                continue

            masked_value = redact(raw_value)
            finding_key = (pii_type, masked_value)
            if finding_key in seen:
                continue

            occupied_spans.append((match.start(), match.end()))
            seen.add(finding_key)
            findings.append(
                {
                    "pii_type": pii_type,
                    "redacted_value": masked_value,
                    "confidence_score": 95.00,
                    "location_reference": f"character {match.start() + 1}",
                }
            )

    return findings


def calculate_risk(findings: list[dict[str, object]]) -> tuple[int, str]:
    """Convert detected PII into a capped numeric score and risk label."""
    score = min(100, sum(PII_WEIGHTS[item["pii_type"]] for item in findings))
    if score >= 80:
        return score, "critical"
    if score >= 60:
        return score, "high"
    if score >= 30:
        return score, "medium"
    return score, "low"


def classification_for(risk_level: str) -> str:
    """Map a calculated risk label to the existing document classification."""
    return {
        "critical": "restricted",
        "high": "restricted",
        "medium": "confidential",
        "low": "internal",
    }[risk_level]
