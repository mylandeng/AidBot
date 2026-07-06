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
        text = re.sub(r"(?is)<table[^>]*>(.*?)</table>", lambda match: f"\n{self._parse_html_table(match.group(1))}\n", text)
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

    def _parse_html_table(self, table_html: str) -> str:
        rows: list[list[str]] = []
        for row_match in re.finditer(r"(?is)<tr[^>]*>(.*?)</tr>", table_html):
            cells = [self._strip_inline_html(cell.group(2)) for cell in re.finditer(r"(?is)<(td|th)[^>]*>(.*?)</\1>", row_match.group(1))]
            cells = [cell for cell in cells if cell]
            if cells:
                rows.append(cells)
        if not rows:
            return self._strip_inline_html(table_html)

        lines = [" | ".join(row) for row in rows]
        headers = rows[0]
        for row in rows[1:]:
            if len(row) != len(headers):
                continue
            pairs = [f"{header}：{value}" for header, value in zip(headers, row) if header and value]
            if pairs:
                lines.append("；".join(pairs))
        return "\n".join(lines)

    def _strip_inline_html(self, fragment: str) -> str:
        fragment = re.sub(
            r"(?is)<img[^>]*(?:alt|title)=[\"']([^\"']+)[\"'][^>]*>",
            lambda match: f" {match.group(1)} ",
            fragment,
        )
        stripped = re.sub(r"<[^>]+>", " ", fragment)
        return re.sub(r"\s+", " ", unescape(stripped)).strip()
