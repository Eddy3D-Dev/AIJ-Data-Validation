// Cloudflare Worker: the two things the static sites cannot do themselves (GitHub Pages sets no custom headers).
//   1. Link response headers on the homepage (RFC 8288, RFC 9727 section 3): api-catalog, service-desc, service-doc.
//   2. Content-Type: application/linkset+json on /.well-known/api-catalog (RFC 9727).
//
// Deploy once for all the sites (Workers & Pages > Create > Worker, paste this file), then add a route for each:
//   www.eddy3d.com/*   docs.eddy3d.com/*   aij.eddy3d.com/*
//   patrickkastner.me/*   sustainableurbansystems.com/*
// The hostnames must be proxied (orange cloud). Markdown negotiation is a Cloudflare setting, not code:
// Speed > Optimization > Content Optimization > "Markdown for Agents" (plan permitting).

const AIJ = "https://aij.eddy3d.com";

// The AIJ API is the one public API of the project; the other sites point at it.
const LINKS = {
  "aij.eddy3d.com": [
    '</.well-known/api-catalog>; rel="api-catalog"',
    '</api/openapi.json>; rel="service-desc"; type="application/vnd.oai.openapi+json"',
    '</api-reference/>; rel="service-doc"; type="text/html"',
    '</api/llms.txt>; rel="describedby"; type="text/plain"',
  ],
  default: [
    '</.well-known/api-catalog>; rel="api-catalog"',
    `<${AIJ}/api/openapi.json>; rel="service-desc"; type="application/vnd.oai.openapi+json"`,
    `<${AIJ}/api-reference/>; rel="service-doc"; type="text/html"`,
  ],
};

export default {
  async fetch(request) {
    const response = await fetch(request);
    const url = new URL(request.url);
    const headers = new Headers(response.headers);

    if (url.pathname === "/") {
      headers.set("Link", (LINKS[url.hostname] || LINKS.default).join(", "));
    }
    if (url.pathname === "/.well-known/api-catalog") {
      headers.set("Content-Type", "application/linkset+json");
    }
    return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
  },
};
