import re

from app.schemas.extraction import ExtractedDocument, ExtractionField

KHMER_RANGE = r"[ក-៿]"


def _levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(
                min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2))
            )
        prev = curr
    return prev[-1]


def fuzzy_contains(text: str, keyword: str, max_distance: int = 1) -> bool:
    words = re.findall(r"[A-Za-z]+", text.lower())
    keyword_lower = keyword.lower()
    for word in words:
        if abs(len(word) - len(keyword_lower)) > max_distance:
            continue
        if _levenshtein(word, keyword_lower) <= max_distance:
            return True
    return False


def _extract_document_type(text: str) -> tuple[str | None, float, str]:
    type_keywords = {
        "receipt": ["receipt", "reciept"],
        "invoice": ["invoice", "inv", "invoic"],
        "bill": ["bill"],
    }
    for doc_type, keywords in type_keywords.items():
        for kw in keywords:
            if fuzzy_contains(text, kw, max_distance=1):
                return doc_type, 0.8, "keyword"
    return None, 0.0, ""


LABEL_PATTERNS = [
    r"(?i)receipt\s*id",
    r"(?i)invoice\s*no",
    r"(?i)date",
    r"(?i)total",
    r"(?i)cashier",
    r"(?i)customer",
    r"(?i)phone",
    r"(?i)tel",
    r"(?i)qty",
    r"(?i)price",
    r"(?i)discount",
    r"(?i)grand",
    r"(?i)change",
    r"(?i)thank",
    r"(?i)wifi",
    r"(?i)password",
    r"(?i)www\.",
    r"(?i)@\w+\.",
]


def _extract_company_name(lines: list[dict]) -> tuple[str | None, float, str]:
    company_parts = []
    total_conf = 0.0
    for line in lines:
        line_text = line["text"].strip()
        if not line_text or len(line_text) < 3:
            continue
        if re.search(KHMER_RANGE, line_text) and not re.search(
            r"[A-Za-z]{3,}", line_text
        ):
            continue
        is_label = False
        for pat in LABEL_PATTERNS:
            if re.search(pat, line_text):
                is_label = True
                break
        if is_label:
            break
        if re.match(r"^[\d\.\-/\s]+$", line_text):
            continue
        company_parts.append(line_text)
        total_conf += line.get("confidence", 0.4)
    if not company_parts:
        return None, 0.0, ""
    name = " ".join(company_parts[:2])
    avg_conf = total_conf / len(company_parts)
    return name, min(avg_conf, 1.0), "top_line_rule"


PHONE_PATTERNS = [
    (
        r"(?:Tel|Phone|Tel\.?|Ph)\s*:?\s*"
        r"(0\d{2}[\s\-]?\d{3}[\s\-]?\d{3,4})",
        0.85,
        "regex",
    ),
    (r"\b(0\d{2}[\s\-]?\d{3}[\s\-]?\d{3,4})\b", 0.6, "regex"),
]


def _extract_phone(text: str) -> tuple[str | None, float, str]:
    for pat, conf, source in PHONE_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), conf, source
    return None, 0.0, ""


DATE_LABEL_PATTERN = (
    r"(?:Date\s*/\s*TIME|Date|DATE)\s*:?\s*"
    r"(\d{1,2}[/-]+\d{1,2}[/-]+\d{2,4})"
)

DATE_STANDALONE = [
    (r"\b(\d{1,2}/+\d{1,2}/+\d{4})\b", 0.6, "regex"),
    (r"\b(\d{1,2}-\d{1,2}-\d{4})\b", 0.6, "regex"),
    (r"\b(\d{4}-\d{1,2}-\d{1,2})\b", 0.6, "regex"),
]


def _extract_date(text: str) -> tuple[str | None, float, str]:
    m = re.search(DATE_LABEL_PATTERN, text, re.IGNORECASE)
    if m:
        raw = m.group(1).strip()
        iso = _normalize_date(raw)
        return iso, 0.85, "regex"

    for pat, conf, source in DATE_STANDALONE:
        m = re.search(pat, text)
        if m:
            raw = m.group(1).strip()
            iso = _normalize_date(raw)
            return iso, conf, source
    return None, 0.0, ""


def _normalize_date(raw: str) -> str | None:
    raw = raw.replace("//", "/")
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            from datetime import datetime as dt

            return dt.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw


INVOICE_NUM_PATTERN = (
    r"(?:Receipt\s*ID|Invoice\s*No|Inv\s*No|Receipt)\s*:?\s*"
    r"([A-Za-z0-9/\-]+)"
)


def _extract_invoice_number(text: str) -> tuple[str | None, float, str]:
    m = re.search(INVOICE_NUM_PATTERN, text, re.IGNORECASE)
    if m:
        return m.group(1).strip(), 0.85, "regex"
    return None, 0.0, ""


def _extract_total_amount(text: str) -> tuple[str | None, float, str]:
    riel_pattern = (
        r"(?:Grand\s*To{1,2}tal.*?(?:Riel\w*|KHR).*?)"
        r"(\d[\d,]+\.?\d*)"
    )
    m = re.search(riel_pattern, text, re.IGNORECASE)
    if m:
        return m.group(1).strip(), 0.9, "regex"

    grand_total_patterns = [
        (
            r"(?:Grand\s*To{1,2}tal|Grand\s*Total)\s*:?\s*"
            r"([\d,]+\.?\d*)",
            0.8,
            "regex",
        ),
    ]
    for pat, conf, source in grand_total_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), conf, source

    total_patterns = [
        (r"(?:Total|To{1,2}tal)\s*:?\s*([\d,]+\.?\d*)", 0.6, "regex"),
    ]
    for pat, conf, source in total_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), conf, source
    return None, 0.0, ""


def _extract_currency(
    text: str, total_amount: str | None
) -> tuple[str | None, float, str]:
    if re.search(r"(?:Riel{1,2}|Riell|KHR)", text, re.IGNORECASE):
        return "KHR", 0.9, "keyword"
    if re.search(r"[\$USD]", text):
        return "USD", 0.85, "keyword"
    if total_amount:
        cleaned = total_amount.replace(",", "")
        try:
            val = float(cleaned)
            if val > 100000:
                return "KHR", 0.5, "heuristic"
            return "USD", 0.5, "heuristic"
        except ValueError:
            pass
    return None, 0.0, ""


class ExtractionService:
    def extract(
        self,
        ocr_text: str,
        raw_lines: list[dict],
        document_id: str,
    ) -> ExtractedDocument:
        doc_type, type_conf, type_src = _extract_document_type(ocr_text)
        company, company_conf, company_src = _extract_company_name(raw_lines)
        phone, phone_conf, phone_src = _extract_phone(ocr_text)
        date, date_conf, date_src = _extract_date(ocr_text)
        inv_num, inv_conf, inv_src = _extract_invoice_number(ocr_text)
        total, total_conf, total_src = _extract_total_amount(ocr_text)
        currency, curr_conf, curr_src = _extract_currency(ocr_text, total)

        raw_preview = ocr_text[:500] if ocr_text else ""

        return ExtractedDocument(
            document_id=document_id,
            document_type=ExtractionField(
                value=doc_type, confidence=type_conf, source=type_src
            ),
            company_name=ExtractionField(
                value=company, confidence=company_conf, source=company_src
            ),
            phone=ExtractionField(
                value=phone, confidence=phone_conf, source=phone_src
            ),
            date=ExtractionField(
                value=date, confidence=date_conf, source=date_src
            ),
            invoice_number=ExtractionField(
                value=inv_num, confidence=inv_conf, source=inv_src
            ),
            total_amount=ExtractionField(
                value=total, confidence=total_conf, source=total_src
            ),
            currency=ExtractionField(
                value=currency, confidence=curr_conf, source=curr_src
            ),
            raw_text_preview=raw_preview,
        )
