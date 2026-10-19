// Cloudflare Worker: Markdown for agents, free (Cloudflare's own toggle needs the Pro plan).
//
// A request with `Accept: text/markdown` gets the page's main content as Markdown (Content-Type: text/markdown); every other
// request, and every non-HTML file (the JSON API, CSV, STL, images), passes through untouched. HTML responses gain `Vary: Accept`
// so no cache hands Markdown to a browser.
//
// Deployed 2026-10-19 as the Worker `markdown-negotiation` in the eddy3d.com Cloudflare account, routes www.eddy3d.com/*,
// docs.eddy3d.com/* and aij.eddy3d.com/* (eddy3d.com zone), failure mode "fail open" (an error falls back to the plain site),
// workers.dev address off. Paste this file into the Worker's editor to change it.
//
// The converter reads the page's <main> (or <article>, or <body>), drops navigation, scripts, styles and forms, and keeps
// headings, paragraphs, lists, links, code, tables and images. It is a small tokenizer, not a full HTML parser: the sites it
// serves are generated static HTML (Jekyll, MkDocs), which it handles.

const SKIP = new Set(["script", "style", "nav", "header", "footer", "svg", "button", "noscript", "form", "select", "head", "template", "iframe", "aside", "dialog"]);
const BLOCK = new Set(["div", "section", "tr", "figure", "figcaption", "dl", "dt", "dd", "details", "main", "article"]);
const VOID = new Set(["br", "hr", "img", "input", "meta", "link", "source", "wbr", "col"]);
const ENTITIES = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " ", mdash: "—", ndash: "–", hellip: "…", rarr: "→", larr: "←", times: "×", copy: "©", middot: "·", laquo: "«", raquo: "»" };

const decode = (s) =>
  s.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) => {
    if (e[0] === "#") {
      const n = e[1].toLowerCase() === "x" ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10);
      return Number.isFinite(n) ? String.fromCodePoint(n) : m;
    }
    return ENTITIES[e.toLowerCase()] ?? m;
  });

const attr = (tag, name) => {
  const m = new RegExp(`\\s${name}\\s*=\\s*("([^"]*)"|'([^']*)'|([^\\s>]+))`, "i").exec(tag);
  return m ? decode(m[2] ?? m[3] ?? m[4] ?? "") : "";
};

export function htmlToMarkdown(html, base = "https://example.com/") {
  const region = /<main[\s>][\s\S]*<\/main>/i.exec(html) || /<article[\s>][\s\S]*<\/article>/i.exec(html) || /<body[\s>][\s\S]*<\/body>/i.exec(html);
  const src = (region ? region[0] : html).replace(/<!--[\s\S]*?-->/g, "");
  const resolve = (u) => { try { return new URL(u, base).href; } catch { return u; } };

  let out = "";                       // the current buffer (a table cell swaps it)
  const saved = [];                   // buffers of the cells being filled
  const lists = [];                   // {ordered, n}
  const links = [];                   // href per open <a> ("" for none)
  let skip = null, skipDepth = 0, pre = false, rows = null, row = null, quote = 0, trimNext = false;

  const emit = (s) => { out += s; };
  const open = (s) => { emit(s); trimNext = true; };                      // an opener: the text after it starts flush
  const close = (s) => { out = out.replace(/[ \t]+$/, ""); emit(s); };    // a closer: the text before it ends flush
  const para = () => { if (!/\n\n$/.test(out) && out) out = out.replace(/[ \t]+$/, "") + "\n\n"; };
  const nl = () => { if (!/\n$/.test(out) && out) out = out.replace(/[ \t]+$/, "") + "\n"; };
  const prefix = () => (quote ? "> ".repeat(quote) : "");

  const re = /<(\/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*)>|([^<]+)|</g;
  let m;
  while ((m = re.exec(src))) {
    if (m[4] !== undefined) {                                   // text
      if (skip) continue;
      if (pre) { emit(decode(m[4])); continue; }
      let t = decode(m[4]).replace(/\s+/g, " ");
      if (trimNext || !out || /\s$/.test(out)) t = t.replace(/^ /, "");
      trimNext = false;
      if (t) { if (/\n$/.test(out) && prefix()) emit(prefix()); emit(t); }
      continue;
    }
    if (m[2] === undefined) continue;
    const closing = m[1] === "/", tag = m[2].toLowerCase(), raw = m[3] || "";
    if (skip) {                                                  // inside a dropped element: only count its own name
      if (tag === skip && !VOID.has(tag)) { skipDepth += closing ? -1 : 1; if (skipDepth === 0) skip = null; }
      continue;
    }
    if (!closing && SKIP.has(tag)) { skip = tag; skipDepth = 1; continue; }

    if (tag === "pre") {
      if (!closing) { para(); emit("```\n"); pre = true; } else { pre = false; nl(); emit("```"); para(); }
    } else if (tag === "code") {
      if (!pre) { if (!closing) open("`"); else close("`"); }
    } else if (/^h[1-6]$/.test(tag)) {
      if (!closing) { para(); open("#".repeat(+tag[1]) + " "); } else { para(); }
    } else if (tag === "p" || tag === "ul" || tag === "ol" || tag === "table" || tag === "blockquote") {
      if (tag === "ul" || tag === "ol") {
        if (!closing) { lists.push({ ordered: tag === "ol", n: 0 }); nl(); } else { lists.pop(); if (!lists.length) para(); }
      } else if (tag === "table") {
        if (!closing) { rows = []; para(); } else { emit(renderTable(rows)); rows = null; para(); }
      } else if (tag === "blockquote") {
        if (!closing) { para(); quote++; emit("> "); } else { quote--; para(); }
      } else { para(); }
    } else if (tag === "li") {
      if (!closing) {
        const l = lists[lists.length - 1];
        nl();
        if (l) { l.n++; emit("  ".repeat(lists.length - 1) + (l.ordered ? `${l.n}. ` : "- ")); } else emit("- ");
      }
    } else if (tag === "br") {
      emit(rows ? " " : "  \n");
    } else if (tag === "hr") {
      para(); emit("---"); para();
    } else if (tag === "strong" || tag === "b") {
      if (!closing) open("**"); else close("**");
    } else if (tag === "em" || tag === "i") {
      if (!closing) open("*"); else close("*");
    } else if (tag === "summary") {
      if (!closing) { para(); open("**"); } else { close("**"); para(); }
    } else if (tag === "a") {
      if (!closing) {
        const href = attr(raw, "href");
        const real = href && !href.startsWith("#") && !/^javascript:/i.test(href);
        links.push(real ? resolve(href) : "");
        if (real) open("[");
      } else {
        const href = links.pop();
        if (href) close(`](${href})`);
      }
    } else if (tag === "img") {
      const s = attr(raw, "src");
      if (s && !s.startsWith("data:")) emit(`![${attr(raw, "alt")}](${resolve(s)})`);
    } else if (tag === "tr") {
      if (rows) { if (!closing) { row = []; } else { rows.push(row); row = null; } }
    } else if (tag === "th" || tag === "td") {
      if (!closing) { saved.push(out); out = ""; } else if (saved.length) {
        const cell = out.replace(/\s*\n+\s*/g, " ").replace(/\|/g, "\\|").trim();
        out = saved.pop();
        if (row) row.push(cell);
      }
    } else if (BLOCK.has(tag)) {
      nl();
    }
    if (closing && (tag === "p" || tag === "li")) { if (tag === "p") para(); }
  }
  const text = out
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .replace(/\*\*\s*\*\*/g, "")
    .trim();
  return text + "\n";
}

function renderTable(rows) {
  rows = rows.filter((r) => r.length);
  if (!rows.length) return "";
  const width = Math.max(...rows.map((r) => r.length));
  const line = (r) => "| " + Array.from({ length: width }, (_, i) => r[i] ?? "").join(" | ") + " |";
  return [line(rows[0]), "|" + " --- |".repeat(width), ...rows.slice(1).map(line)].join("\n");
}

const wantsMarkdown = (accept) =>
  accept.split(",").some((part) => {
    const [type, ...params] = part.trim().split(";");
    if (type.trim().toLowerCase() !== "text/markdown") return false;
    const q = params.map((p) => p.trim()).find((p) => p.startsWith("q="));
    return !q || parseFloat(q.slice(2)) > 0;
  });

export default {
  async fetch(request) {
    const response = await fetch(request);
    const isHtml = (response.headers.get("content-type") || "").toLowerCase().startsWith("text/html");
    if (!isHtml || response.status !== 200) return response;
    if (request.method !== "GET" && request.method !== "HEAD") return response;

    if (wantsMarkdown(request.headers.get("accept") || "")) {
      const markdown = htmlToMarkdown(await response.text(), request.url);
      return new Response(request.method === "HEAD" ? null : markdown, {
        status: 200,
        headers: {
          "content-type": "text/markdown; charset=utf-8",
          vary: "Accept",
          "cache-control": response.headers.get("cache-control") || "public, max-age=600",
          "x-markdown-source": "html",
        },
      });
    }
    const passthrough = new Response(response.body, response);
    passthrough.headers.append("vary", "Accept");
    return passthrough;
  },
};
