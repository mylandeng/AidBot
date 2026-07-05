import re
from html import unescape

from fastapi import HTTPException, status

from app.schemas.knowledge import ContentFormat


class DocumentService:
    def parse_text(self, content: str, content_format: ContentFormat) -> str:
        if content_format in {"markdown", "text"}:
            return content.strip()
        if content_format == "html":
            return self._parse_html(content)
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="PDF parsing is not enabled yet")

    def _parse_html(self, content: str) -> str:
        text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", content)
        text = re.sub(
            r"(?is)<h([1-6])[^>]*>(.*?)</h\1>",
            lambda match: f"\n{'#' * int(match.group(1))} {self._strip_inline_html(match.group(2))}\n",
            text,
        )
        text = re.sub(r"(?is)<li[^>]*>(.*?)</li>", lambda match: f"\n- {self._strip_inline_html(match.group(1))}\n", text)
        text = re.sub(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", lambda match: f" {self._strip_inline_html(match.group(1))} ", text)
        text = re.sub(r"(?i)<br\s*/?>", "\n", text)
        text = re.sub(r"(?i)</(p|div|section|article|tr|table|ul|ol)>", "\n", text)
        text = re.sub(r"<[^>]+>", " ", text)
        lines = [re.sub(r"\s+", " ", unescape(line)).strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line)

    def _strip_inline_html(self, fragment: str) -> str:
        stripped = re.sub(r"<[^>]+>", " ", fragment)
        return re.sub(r"\s+", " ", unescape(stripped)).strip()
