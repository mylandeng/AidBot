"use client";

type Block =
  | { type: "paragraph"; lines: string[] }
  | { type: "heading"; level: number; text: string }
  | { type: "quote"; lines: string[] }
  | { type: "code"; language: string; text: string }
  | { type: "list"; ordered: boolean; items: string[] }
  | { type: "table"; rows: string[][] };

export function MessageContent({ content, markdown = false }: { content: string; markdown?: boolean }) {
  if (!markdown) {
    return <p className="message-plain">{content}</p>;
  }

  const blocks = parseMarkdown(content);
  return (
    <div className="message-markdown">
      {blocks.map((block, index) => {
        if (block.type === "heading") {
          const Tag = `h${Math.min(block.level, 4)}` as "h1" | "h2" | "h3" | "h4";
          return <Tag key={index}>{renderInline(block.text)}</Tag>;
        }
        if (block.type === "quote") {
          return (
            <blockquote key={index}>
              {block.lines.map((line, lineIndex) => (
                <p key={lineIndex}>{renderInline(line)}</p>
              ))}
            </blockquote>
          );
        }
        if (block.type === "code") {
          return (
            <pre key={index}>
              <code>{block.text}</code>
            </pre>
          );
        }
        if (block.type === "list") {
          const ListTag = block.ordered ? "ol" : "ul";
          return (
            <ListTag key={index}>
              {block.items.map((item, itemIndex) => (
                <li key={itemIndex}>{renderInline(item)}</li>
              ))}
            </ListTag>
          );
        }
        if (block.type === "table") {
          const [head, ...body] = block.rows;
          return (
            <div className="markdown-table-wrap" key={index}>
              <table>
                {head ? (
                  <thead>
                    <tr>
                      {head.map((cell, cellIndex) => (
                        <th key={cellIndex}>{renderInline(cell)}</th>
                      ))}
                    </tr>
                  </thead>
                ) : null}
                <tbody>
                  {body.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      {row.map((cell, cellIndex) => (
                        <td key={cellIndex}>{renderInline(cell)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }
        return (
          <p key={index}>
            {block.lines.map((line, lineIndex) => (
              <span key={lineIndex}>
                {lineIndex > 0 ? <br /> : null}
                {renderInline(line)}
              </span>
            ))}
          </p>
        );
      })}
    </div>
  );
}

function parseMarkdown(content: string): Block[] {
  const lines = content.replace(/\r\n/g, "\n").split("\n");
  const blocks: Block[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];
    if (!line.trim()) {
      index += 1;
      continue;
    }

    const fence = line.match(/^\s*```(\w+)?\s*$/);
    if (fence) {
      const codeLines: string[] = [];
      index += 1;
      while (index < lines.length && !/^\s*```\s*$/.test(lines[index])) {
        codeLines.push(lines[index]);
        index += 1;
      }
      blocks.push({ type: "code", language: fence[1] ?? "", text: codeLines.join("\n") });
      index += 1;
      continue;
    }

    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      blocks.push({ type: "heading", level: heading[1].length, text: heading[2].trim() });
      index += 1;
      continue;
    }

    if (/^\s*>\s?/.test(line)) {
      const quoteLines: string[] = [];
      while (index < lines.length && /^\s*>\s?/.test(lines[index])) {
        quoteLines.push(lines[index].replace(/^\s*>\s?/, ""));
        index += 1;
      }
      blocks.push({ type: "quote", lines: quoteLines });
      continue;
    }

    if (isTableStart(lines, index)) {
      const rows: string[][] = [];
      rows.push(splitTableRow(lines[index]));
      index += 2;
      while (index < lines.length && /^\s*\|.*\|\s*$/.test(lines[index])) {
        rows.push(splitTableRow(lines[index]));
        index += 1;
      }
      blocks.push({ type: "table", rows });
      continue;
    }

    const listMatch = line.match(/^\s*(?:([-*+])|(\d+)[.)])\s+(.+)$/);
    if (listMatch) {
      const ordered = Boolean(listMatch[2]);
      const items: string[] = [];
      while (index < lines.length) {
        const itemMatch = lines[index].match(/^\s*(?:([-*+])|(\d+)[.)])\s+(.+)$/);
        if (!itemMatch || Boolean(itemMatch[2]) !== ordered) break;
        items.push(itemMatch[3].trim());
        index += 1;
      }
      blocks.push({ type: "list", ordered, items });
      continue;
    }

    const paragraph: string[] = [];
    while (index < lines.length && lines[index].trim()) {
      if (/^\s*```/.test(lines[index]) || /^(#{1,6})\s+/.test(lines[index])) break;
      if (/^\s*>\s?/.test(lines[index]) || /^\s*(?:[-*+]|\d+[.)])\s+/.test(lines[index])) break;
      if (isTableStart(lines, index)) break;
      paragraph.push(lines[index].trim());
      index += 1;
    }
    blocks.push({ type: "paragraph", lines: paragraph });
  }

  return blocks;
}

function isTableStart(lines: string[], index: number): boolean {
  return /^\s*\|.*\|\s*$/.test(lines[index] ?? "") && /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(lines[index + 1] ?? "");
}

function splitTableRow(line: string): string[] {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

function renderInline(text: string) {
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*|__[^_]+__|\[[^\]]+\]\([^)]+\))/g).filter(Boolean);
  return parts.map((part, index) => {
    if (part.startsWith("`") && part.endsWith("`")) {
      return <code key={index}>{part.slice(1, -1)}</code>;
    }
    if ((part.startsWith("**") && part.endsWith("**")) || (part.startsWith("__") && part.endsWith("__"))) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    const link = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (link && /^https?:\/\//.test(link[2])) {
      return (
        <a href={link[2]} key={index} rel="noreferrer" target="_blank">
          {link[1]}
        </a>
      );
    }
    return part;
  });
}
