#!/usr/bin/env python3
"""Verify job-posting URLs are live and durable.

Usage:
    python3 scripts/verify_urls.py "<url1>" "<url2>" ...

For each URL it follows redirects and reports:
    OK       2xx and the final URL still looks like a specific posting
    REDIRECT landed somewhere that looks like a careers index / search page
    DEAD     4xx / 5xx / connection error
    CLOSED   page body says the position is closed / no longer available

Exit code is 0 if every URL is OK, else 1. Use this before putting a URL in a packet.
This is a heuristic gate, not a guarantee. WebFetch the survivors for a deeper check.
"""
import sys
import urllib.request
import urllib.error

INDEX_HINTS = (
    "/careers", "/jobs?", "job-search", "jobsearch", "all-jobs",
    "/job-openings", "joinus", "/careerpage", "career-site",
)
CLOSED_HINTS = (
    "no longer available", "position closed", "this job is closed",
    "posting is closed", "0 jobs", "no jobs found", "job not found",
    "we couldn't find", "page not found",
)
# A trailing index path with no specific id is a weak (index) URL even on 200.
SPECIFIC_HINTS = ("jk=", "/jobs/view/", "/jobs/", "/job/", "greenhouse.io/", "lever.co/",
                  "ashbyhq.com/", "myworkdayjobs.com/", "turbohire.co/careerpage/")


def check(url: str) -> tuple[str, str]:
    # Indeed aggressively blocks automated requests (403/captcha). Its links come from
    # the Indeed MCP, which is its own live API, so trust them by source rather than
    # false-flagging here. The verifier is for non-Indeed ATS / careers URLs.
    low = url.lower()
    if "indeed.com" in low:
        return "TRUSTED", "Indeed link (validated by the Indeed MCP at source, not re-fetched)"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (CareerOPS URL verifier)"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            final = resp.geturl()
            body = resp.read(60000).decode("utf-8", "ignore").lower()
    except urllib.error.HTTPError as e:
        return "DEAD", f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001
        return "DEAD", f"{type(e).__name__}: {e}"

    for hint in CLOSED_HINTS:
        if hint in body:
            return "CLOSED", f"body mentions '{hint}'"

    low_final = final.lower()
    looks_specific = any(h in low_final for h in SPECIFIC_HINTS)
    looks_index = any(h in low_final for h in INDEX_HINTS)
    if looks_index and not looks_specific:
        return "REDIRECT", f"final URL looks like an index: {final}"
    return "OK", final


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    all_ok = True
    for url in argv:
        status, detail = check(url)
        if status not in ("OK", "TRUSTED"):
            all_ok = False
        print(f"{status:9} {url}\n          -> {detail}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
