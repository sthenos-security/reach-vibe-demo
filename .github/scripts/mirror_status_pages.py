#!/usr/bin/env python3
# Copyright © 2026 Sthenos Security. All rights reserved.
"""Copy the four published status pages onto this repo's own public site.

The pages are the demo hub and one status page per agent. They are produced by a
private runner -- private because it holds the vendor keys and the application
seed -- whose Pages site is the only public thing it emits. Partners and
investors should be able to land on a page served out of a repository they can
read end to end, so this copies those four pages here and leaves every deeper
evidence link (before/after scans, code viewers, diffs) pointing at the source
site, which is already public and stays the system of record.

Nothing here is authenticated. The pages are fetched over plain HTTPS exactly as
a visitor fetches them, so this script cannot reach anything in the private
repository that a visitor could not.

Two rewrites are applied to each copied page, and they are the whole reason this
is a script rather than `curl -o`:

1. **Links.** A relative link in a copied page would otherwise resolve against
   *this* site, where only these four pages exist. Every relative link is
   resolved against its source page and then either kept local (when it points
   at one of the four pages we copy) or made absolute against the source site.
2. **Workflow-run links.** The source pages link their GitHub Actions run, which
   lives in the private repository and therefore 404s for every reader. The run
   id is provenance worth keeping, so the link becomes plain text and the id
   stays.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

DEFAULT_SOURCE = "https://sthenos-security.github.io/reach-vibe-throwdown"

#: The agents that own a status page. Explicit, not discovered: a lane that has
#: stopped publishing must produce a visible failure here, not a site that is
#: quietly missing a page.
LANES = ("codex", "claude", "cursor")

_ATTR = re.compile(r'\b(?P<attr>href|src)="(?P<url>[^"]*)"')

#: A link into a workflow run, in any repository. Matched non-greedily and with
#: DOTALL because the anchor text in these pages is wrapped across lines.
_RUN_LINK = re.compile(
    r'<a\b[^>]*href="https://[^"]*/actions/runs/(?P<run>\d+)[^"]*"[^>]*>(?P<text>.*?)</a>',
    re.S,
)


def canonical(url: str) -> str:
    """Return `url` in the one form used to compare it with a mirrored page.

    `…/codex/`, `…/codex`, and `…/codex/index.html` are the same page and all
    three appear in these pages' markup.
    """
    url = url.split("#", 1)[0]
    if url.endswith("/index.html"):
        url = url[: -len("index.html")]
    if not url.endswith("/"):
        url += "/"
    return url


def page_map(source: str) -> dict[str, str]:
    """Return {canonical source URL: local path} for the four copied pages."""
    base = source.rstrip("/") + "/"
    pages = {canonical(base): "index.html"}
    for lane in LANES:
        pages[canonical(urljoin(base, f"{lane}/"))] = f"{lane}/index.html"
    return pages


def _relative(from_page: str, to_page: str) -> str:
    """Path from one copied page to another, as a browser resolves it."""
    return os.path.relpath(to_page, os.path.dirname(from_page)).replace(os.sep, "/")


def rewrite(html: str, *, page_url: str, local_path: str, source: str,
            pages: dict[str, str], fetched_at: str) -> str:
    """Return `html` with links repointed and private run links neutralised."""
    base = source.rstrip("/") + "/"

    def _neutralise_run(match: re.Match[str]) -> str:
        # The anchor text carries the sentence the page was written around
        # ("this pipeline run", "Run 32653969163"), so it is kept verbatim and
        # only the link is dropped. The hub already prints the id in that text;
        # repeating it as "Run 1234 (private run 1234)" reads like a defect.
        text = " ".join(match.group("text").split())
        run = match.group("run")
        if run in text:
            return text
        return f'{text} <span class="muted">(private run {run})</span>'

    html = _RUN_LINK.sub(_neutralise_run, html)

    def _repoint(match: re.Match[str]) -> str:
        url = match.group("url")
        if not url or url.startswith(("#", "mailto:", "data:", "javascript:")):
            return match.group(0)
        absolute = urljoin(page_url, url)
        if not absolute.startswith(base):
            # Already elsewhere -- another site, or the source site's parent.
            # Left exactly as the page had it.
            return match.group(0)
        target = pages.get(canonical(absolute))
        replacement = _relative(local_path, target) if target else absolute
        return f'{match.group("attr")}="{replacement}"'

    html = _ATTR.sub(_repoint, html)

    provenance = (
        '<p class="muted" style="font-size:12px;margin-top:28px">Copied from '
        f'<a href="{page_url}">{page_url}</a> at {fetched_at}. '
        "The evidence pages this links into are served from that site.</p>"
    )
    if "</body>" in html:
        html = html.replace("</body>", f"{provenance}</body>", 1)
    else:
        html += provenance
    return f"<!-- copied from {page_url} at {fetched_at} -->\n{html}"


def fetch(url: str, *, attempts: int, delay: float) -> str:
    """GET `url`, retrying while the source site is mid-deployment.

    A publish on the source side replaces its whole site, so a copy started
    seconds after a demo finishes can arrive during that window and read a 404.
    Retrying is the difference between "the page is gone" and "the page is being
    written", and only the first is worth failing on.
    """
    last = ""
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return response.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last = str(exc)
            print(f"attempt {attempt}/{attempts} for {url}: {last}", file=sys.stderr)
            if attempt < attempts:
                time.sleep(delay)
    raise SystemExit(f"error: could not fetch {url} after {attempts} attempts: {last}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=DEFAULT_SOURCE,
                        help="status-page site to copy from")
    parser.add_argument("--output", type=Path, required=True,
                        help="directory to write the copied site into")
    parser.add_argument("--attempts", type=int, default=10)
    parser.add_argument("--retry-delay", type=float, default=30.0)
    args = parser.parse_args(argv)

    source = args.source.rstrip("/")
    pages = page_map(source)
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    for page_url, local_path in pages.items():
        html = fetch(page_url, attempts=args.attempts, delay=args.retry_delay)
        # A status page that came back as an error page is worse than a missing
        # one: it publishes as though the lane had reported something.
        if "<html" not in html.lower():
            raise SystemExit(f"error: {page_url} did not return HTML")
        rewritten = rewrite(html, page_url=page_url, local_path=local_path,
                            source=source, pages=pages, fetched_at=fetched_at)
        destination = args.output / local_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rewritten, encoding="utf-8")
        print(f"{page_url} -> {destination} ({len(rewritten)} bytes)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
