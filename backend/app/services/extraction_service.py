import re
from app.schemas.extraction import ExtractedDocument


def _levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
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


def _extract_document_type(text: str) -> tuple[str | None, float]:
    type_keywords = {
        "receipt": ["receipt", "reciept"],
        "invoice": ["invoice", "inv", "invoic"],
        "bill": ["bill"],
    }
    for doc_type, keywords in type_keywords.items():
        for kw in keywords:
            if fuzzy_contains(text, kw, max_distance=1):
                return doc_type, 0.8
    return None, 0.0


def _extract_company_name(lines: list[dict]) -> tuple[str | None, float]:
    label_patterns = [
        r"(?i)receipt\s*id", r"(?i)invoice\s*no", r"(?i)date",
        r"(?i)total", r"(?i)cashier", r"(?i)customer", r"(?i)phone",
        r"(?i)tel", r"(?i)qty", r"(?i)price", r"(?i)discount",
        r"(?i)grand", r"(?i)change", r"(?i)thank", r"(?i)wifi",
        r"(?i)password", r"(?i)www\.", r"(?i)@\w+\.",
    ]
    company_parts = []
    total_conf = 0.0
    for line in lines:
        line_text = line["text"].strip()
        if not line_text or len(line_text) < 3:
            continue
        if re.search(r"[ក-៿]", line_text) and not re.search(r"[A-Za-z]{3,}", line_text):
            continue
        is_label = False
        for pat in label_patterns:
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
        return None, 0.0
    name = " ".join(company_parts[:2])
    avg_conf = total_conf / len(company_parts)
    return name, min(avg_conf, 1.0)


def _extract_phone(text: str) -> tuple[str | None, float]:
    patterns = [
        (r"(?:Tel|Phone|Tel\.?|Ph)\s*:?\s*(0\d{2}[\s\-]?\d{3}[\s\-]?\d{3,4})", 0.85),
        (r"\b(0\d{2}[\s\-]?\d{3}[\s\-]?\d{3,4})\b", 0.6),
    ]
    for pat, conf in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), conf
    return None, 0.0


def _extract_date(text: str) -> tuple[str | None, float]:
    label_patterns = [
        (r"(?:Date\s*/\s*TIME|Date|DATE)\s*:?\s*(\d{1,2}[/-]+\d{1,2}[/-]+\d{2,4})", 0.85),
    ]
    for pat, conf in label_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            raw = m.group(1).strip()
            iso = _normalize_date(raw)
            return iso, conf

    standalone = [
        (r"\b(\d{1,2}/+\d{1,2}/+\d{4})\b", 0.6),
        (r"\b(\d{1,2}-\d{1,2}-\d{4})\b", 0.6),
        (r"\b(\d{4}-\d{1,2}-\d{1,2})\b", 0.6),
    ]
    for pat, conf in standalone:
        m = re.search(pat, text)
        if m:
            raw = m.group(1).strip()
            iso = _normalize_date(raw)
            return iso, conf
    return None, 0.0


def _normalize_date(raw: str) -> str | None:
    raw = raw.replace("//", "/")
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            from datetime import datetime as dt
            return dt.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw


def _extract_invoice_number(text: str) -> tuple[str | None, float]:
    patterns = [
        (r"(?:Receipt\s*ID|Invoice\s*No|Inv\s*No|Receipt)\s*:?\s*([A-Za-z0-9/\-]+)", 0.85),
    ]
    for pat, conf in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), conf
    return None, 0.0


def _extract_total_amount(text: str) -> tuple[str | None, float]:
    riel_pattern = r"(?:Grand\s*To{1,2}tal.*?(?:Riel\w*|KHR).*?)(\d[\d,]+\.?\d*)"
    m = re.search(riel_pattern, text, re.IGNORECASE)
    if m:
        return m.group(1).strip(), 0.9

    grand_total_patterns = [
        (r"(?:Grand\s*To{1,2}tal|Grand\s*Total)\s*:?\s*([\d,]+\.?\d*)", 0.8),
    ]
    for pat, conf in grand_total_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), conf

    total_patterns = [
        (r"(?:Total|To{1,2}tal)\s*:?\s*([\d,]+\.?\d*)", 0.6),
    ]
    for pat, conf in total_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), conf
    return None, 0.0


def _extract_currency(text: str, total_amount: str | None) -> tuple[str | None, float]:
    if re.search(r"(?:Riel{1,2}|Riell|KHR)", text, re.IGNORECASE):
        return "KHR", 0.85
    if re.search(r"[\$USD]", text):
        return "USD", 0.85
    if total_amount:
        cleaned = total_amount.replace(",", "")
        try:
            val = float(cleaned)
            if val > 100000:
                return "KHR", 0.5
            return "USD", 0.5
        except ValueError:
            pass
    return None, 0.0


class ExtractionService:
    def extract(self, ocr_text: str, raw_lines: list[dict], document_id: str) -> ExtractedDocument:
        doc_type, type_conf = _extract_document_type(ocr_text)
        company, company_conf = _extract_company_name(raw_lines)
        phone, phone_conf = _extract_phone(ocr_text)
        date, date_conf = _extract_date(ocr_text)
        inv_num, inv_conf = _extract_invoice_number(ocr_text)
        total, total_conf = _extract_total_amount(ocr_text)
        currency, curr_conf = _extract_currency(ocr_text, total)

        field_confs = [type_conf, company_conf, phone_conf, date_conf, inv_conf, total_conf, curr_conf]
        found_count = sum(1 for v, c in [(doc_type, type_conf), (company, company_conf), (phone, phone_conf), (date, date_conf), (inv_num, inv_conf), (total, total_conf), (currency, curr_conf)] if v is not None)
        total_fields = 7
        overall = (sum(field_confs) / total_fields) if total_fields > 0 else 0.0

        return ExtractedDocument(
            document_id=document_id,
            document_type=doc_type,
            company_name=company,
            phone=phone,
            date=date,
            invoice_number=inv_num,
            total_amount=total,
            currency=currency,
            confidence=round(overall, 2),
        )