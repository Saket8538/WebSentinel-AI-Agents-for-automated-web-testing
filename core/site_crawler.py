"""
Multi-Page Site Crawler
Discovers and crawls pages within a website, running tests on each discovered page.
BFS-based with domain restriction, robots.txt awareness, and configurable limits.
"""
import asyncio
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urlparse, urljoin, urldefrag
from datetime import datetime


class SiteCrawler:
    """
    BFS-based website crawler that discovers links within the same domain.

    Usage:
        crawler = SiteCrawler(max_pages=20, max_depth=3)
        pages = await crawler.crawl(start_url, page)
    """

    def __init__(
        self,
        max_pages: int = 10,
        max_depth: int = 3,
        respect_robots: bool = True,
        exclude_patterns: Optional[List[str]] = None,
    ):
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.respect_robots = respect_robots
        self.exclude_patterns = exclude_patterns or [
            r'\.(jpg|jpeg|png|gif|svg|ico|webp|pdf|zip|tar|gz|mp4|mp3|avi)$',
            r'(logout|signout|delete|remove)',
            r'#',
            r'mailto:',
            r'tel:',
            r'javascript:',
        ]
        self.visited: Set[str] = set()
        self.discovered_pages: List[Dict[str, Any]] = []
        self.disallowed_paths: Set[str] = set()

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragment and trailing slash."""
        url, _ = urldefrag(url)
        url = url.rstrip('/')
        return url

    def _is_same_domain(self, url: str, base_domain: str) -> bool:
        """Check if URL belongs to the same domain."""
        try:
            parsed = urlparse(url)
            return parsed.netloc == base_domain or parsed.netloc == ''
        except Exception:
            return False

    def _should_exclude(self, url: str) -> bool:
        """Check if URL matches any exclusion pattern."""
        for pattern in self.exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False

    async def _fetch_robots_txt(self, base_url: str, page) -> None:
        """Try to parse robots.txt for disallow rules."""
        if not self.respect_robots:
            return
        try:
            robots_url = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}/robots.txt"
            response = await page.goto(robots_url, wait_until='domcontentloaded', timeout=5000)
            if response and response.status == 200:
                text = await page.content()
                # Simple extraction of Disallow rules for *
                in_wildcard = False
                for line in text.split('\n'):
                    line = line.strip()
                    if line.lower().startswith('user-agent:'):
                        agent = line.split(':', 1)[1].strip()
                        in_wildcard = agent == '*'
                    elif in_wildcard and line.lower().startswith('disallow:'):
                        path = line.split(':', 1)[1].strip()
                        if path:
                            self.disallowed_paths.add(path)
        except Exception:
            pass  # robots.txt not available — proceed without it

    def _is_disallowed(self, url: str) -> bool:
        """Check if URL is disallowed by robots.txt."""
        path = urlparse(url).path
        for disallowed in self.disallowed_paths:
            if path.startswith(disallowed):
                return True
        return False

    async def crawl(self, start_url: str, page) -> List[Dict[str, Any]]:
        """
        Crawl website starting from start_url using BFS.

        Args:
            start_url: The starting URL
            page: Playwright Page object for navigation

        Returns:
            List of discovered page dicts with url, title, depth, status
        """
        self.visited.clear()
        self.discovered_pages.clear()
        self.disallowed_paths.clear()

        start_url = self._normalize_url(start_url)
        base_parsed = urlparse(start_url)
        base_domain = base_parsed.netloc

        # Fetch robots.txt
        await self._fetch_robots_txt(start_url, page)

        # BFS queue: (url, depth)
        queue: List[tuple] = [(start_url, 0)]
        self.visited.add(start_url)

        while queue and len(self.discovered_pages) < self.max_pages:
            current_url, depth = queue.pop(0)

            if depth > self.max_depth:
                continue

            if self._is_disallowed(current_url):
                continue

            # Navigate to page
            try:
                response = await page.goto(
                    current_url, wait_until='domcontentloaded', timeout=15000
                )
                status_code = response.status if response else 0
                title = await page.title() or ''
            except Exception as e:
                self.discovered_pages.append({
                    "url": current_url,
                    "title": "",
                    "depth": depth,
                    "status_code": 0,
                    "error": str(e),
                })
                continue

            self.discovered_pages.append({
                "url": current_url,
                "title": title[:100],
                "depth": depth,
                "status_code": status_code,
            })

            # Don't explore links beyond max_depth - 1
            if depth >= self.max_depth:
                continue

            # Extract links
            try:
                links = await page.eval_on_selector_all(
                    'a[href]',
                    'elements => elements.map(e => e.href)'
                )
            except Exception:
                links = []

            for link in links:
                normalized = self._normalize_url(link)
                if (
                    normalized not in self.visited
                    and self._is_same_domain(normalized, base_domain)
                    and not self._should_exclude(normalized)
                    and normalized.startswith(('http://', 'https://'))
                ):
                    self.visited.add(normalized)
                    queue.append((normalized, depth + 1))

        return self.discovered_pages

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of crawl results."""
        if not self.discovered_pages:
            return {"status": "not_started", "total_pages": 0}

        errors = [p for p in self.discovered_pages if p.get("error")]
        return {
            "status": "complete",
            "total_pages": len(self.discovered_pages),
            "successful": len(self.discovered_pages) - len(errors),
            "errors": len(errors),
            "max_depth_reached": max(p["depth"] for p in self.discovered_pages),
            "pages": [
                {"url": p["url"], "title": p.get("title", ""), "status": p.get("status_code", 0)}
                for p in self.discovered_pages
            ]
        }
