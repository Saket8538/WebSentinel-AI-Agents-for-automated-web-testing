"""
Lighthouse Integration Runner
Runs Google Lighthouse audits via the CLI and parses results.
Falls back gracefully when lighthouse is not installed.
"""
import asyncio
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class LighthouseRunner:
    """
    Run Google Lighthouse audits programmatically.

    Requires `lighthouse` CLI installed via npm:
        npm install -g lighthouse

    Falls back gracefully if not available.

    Usage:
        runner = LighthouseRunner()
        results = await runner.run_audit("https://example.com")
    """

    def __init__(self, chrome_flags: Optional[str] = None):
        self.chrome_flags = chrome_flags or '--headless --no-sandbox --disable-gpu'
        self._lighthouse_available: Optional[bool] = None

    def _check_lighthouse_installed(self) -> bool:
        """Check if the lighthouse CLI is installed."""
        if self._lighthouse_available is not None:
            return self._lighthouse_available

        try:
            result = subprocess.run(
                ['npx', 'lighthouse', '--version'],
                capture_output=True, text=True, timeout=30,
                shell=True  # needed on Windows
            )
            self._lighthouse_available = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            self._lighthouse_available = False

        return self._lighthouse_available

    async def run_audit(
        self,
        url: str,
        categories: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Run a Lighthouse audit on the given URL.

        Args:
            url: The URL to audit
            categories: List of categories to audit
                        (default: performance, accessibility, best-practices, seo)

        Returns:
            Dict with scores and audit details, or a fallback result on failure.
        """
        if not self._check_lighthouse_installed():
            return self._fallback_result(url, "Lighthouse CLI not installed (run 'npm install -g lighthouse')")

        if categories is None:
            categories = ['performance', 'accessibility', 'best-practices', 'seo']

        # Create a temp file for JSON output
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as tmp:
            output_path = tmp.name

        try:
            category_flags = ' '.join(f'--only-categories={c}' for c in categories)
            cmd = (
                f'npx lighthouse "{url}" '
                f'--output=json '
                f'--output-path="{output_path}" '
                f'--chrome-flags="{self.chrome_flags}" '
                f'{category_flags} '
                f'--quiet'
            )

            # Run lighthouse in a subprocess
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=120
            )

            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='replace')[:200]
                return self._fallback_result(url, f"Lighthouse exited with code {process.returncode}: {error_msg}")

            # Parse JSON output
            output_file = Path(output_path)
            if not output_file.exists():
                return self._fallback_result(url, "Lighthouse output file not found")

            with open(output_file, 'r', encoding='utf-8') as f:
                lh_data = json.load(f)

            return self._parse_results(url, lh_data)

        except asyncio.TimeoutError:
            return self._fallback_result(url, "Lighthouse audit timed out (>120s)")
        except Exception as e:
            return self._fallback_result(url, str(e))
        finally:
            # Cleanup temp file
            try:
                Path(output_path).unlink(missing_ok=True)
            except Exception:
                pass

    def _parse_results(self, url: str, lh_data: dict) -> Dict[str, Any]:
        """Parse raw Lighthouse JSON into a clean result dict."""
        categories = lh_data.get('categories', {})
        audits = lh_data.get('audits', {})

        scores = {}
        for cat_id, cat_data in categories.items():
            score_raw = cat_data.get('score')
            scores[cat_id] = {
                "score": round(score_raw * 100) if score_raw is not None else None,
                "title": cat_data.get('title', cat_id),
            }

        # Extract key performance metrics
        metrics = {}
        metric_keys = [
            'first-contentful-paint', 'largest-contentful-paint',
            'total-blocking-time', 'cumulative-layout-shift',
            'speed-index', 'interactive',
        ]
        for key in metric_keys:
            audit = audits.get(key, {})
            metrics[key] = {
                "display_value": audit.get('displayValue', 'N/A'),
                "score": round(audit.get('score', 0) * 100) if audit.get('score') is not None else None,
                "numeric_value": audit.get('numericValue'),
            }

        return {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "available": True,
            "lighthouse_version": lh_data.get('lighthouseVersion', 'unknown'),
            "scores": scores,
            "metrics": metrics,
            "overall_score": self._compute_overall(scores),
        }

    def _compute_overall(self, scores: dict) -> int:
        """Compute a weighted overall score from category scores."""
        valid = [s['score'] for s in scores.values() if s['score'] is not None]
        return round(sum(valid) / len(valid)) if valid else 0

    def _fallback_result(self, url: str, reason: str) -> Dict[str, Any]:
        """Return a graceful fallback when Lighthouse is unavailable."""
        return {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "available": False,
            "reason": reason,
            "scores": {},
            "metrics": {},
            "overall_score": None,
        }
