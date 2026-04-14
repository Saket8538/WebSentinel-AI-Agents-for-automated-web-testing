"""
Visual Regression Testing Module
Compares screenshots across test runs to detect UI changes automatically.
Uses PIL for proper pixel-level comparison when available, falls back to byte comparison.
"""
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import json

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFont
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class VisualRegressionTester:
    """Detect visual changes between test runs using pixel-level comparison"""

    def __init__(self, baseline_dir: str = "visual_baselines", threshold: float = 0.05):
        """
        Initialize visual regression tester

        Args:
            baseline_dir: Directory to store baseline images
            threshold: Acceptable difference threshold (0.0-1.0)
        """
        self.baseline_dir = Path(baseline_dir)
        self.baseline_dir.mkdir(exist_ok=True)
        self.threshold = threshold
        self.results = []

    def capture_baseline(self, page_name: str, screenshot_data: bytes) -> Dict[str, Any]:
        """
        Capture baseline image for comparison

        Args:
            page_name: Name/identifier for the page
            screenshot_data: Screenshot bytes data (PNG format)

        Returns:
            Baseline info dictionary
        """
        try:
            baseline_name = f"baseline_{page_name}.png"
            baseline_path = self.baseline_dir / baseline_name

            with open(baseline_path, 'wb') as f:
                f.write(screenshot_data)

            return {
                "status": "baseline_created",
                "baseline_path": str(baseline_path),
                "page_name": page_name,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"status": "error", "reason": str(e)}

    def compare_with_baseline(
        self,
        page_name: str,
        current_screenshot_data: bytes
    ) -> Dict[str, Any]:
        """
        Compare current screenshot with baseline using pixel-level analysis

        Args:
            page_name: Name/identifier for the page
            current_screenshot_data: Screenshot bytes data (PNG format)

        Returns:
            Comparison results dictionary
        """
        try:
            baseline_name = f"baseline_{page_name}.png"
            baseline_path = self.baseline_dir / baseline_name

            if not baseline_path.exists():
                return {
                    "status": "no_baseline",
                    "message": "No baseline found. Run capture_baseline() first.",
                    "page_name": page_name,
                    "passed": False,
                    "difference_percentage": 100.0
                }

            with open(baseline_path, 'rb') as f:
                baseline_data = f.read()

            # Identical bytes => zero difference
            if baseline_data == current_screenshot_data:
                diff_percent = 0.0
                diff_image_path = None
            elif PIL_AVAILABLE:
                # Use PIL for proper pixel-level comparison
                diff_percent, diff_image_path = self._pil_compare(
                    baseline_data, current_screenshot_data, page_name
                )
            else:
                # Fallback: byte-level comparison
                diff_percent = self._byte_compare(baseline_data, current_screenshot_data)
                diff_image_path = None

            is_significant = diff_percent > (self.threshold * 100)

            result = {
                "status": "compared",
                "page_name": page_name,
                "baseline_path": str(baseline_path),
                "difference_percentage": round(diff_percent, 2),
                "threshold_percentage": round(self.threshold * 100, 2),
                "is_significant_change": is_significant,
                "passed": not is_significant,
                "verdict": "FAIL" if is_significant else "PASS",
                "diff_image": diff_image_path,
                "comparison_method": "PIL" if PIL_AVAILABLE else "byte",
                "timestamp": datetime.now().isoformat()
            }

            self.results.append(result)
            return result

        except Exception as e:
            return {
                "status": "error",
                "reason": str(e),
                "page_name": page_name,
                "passed": False
            }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _pil_compare(
        self,
        baseline_data: bytes,
        current_data: bytes,
        page_name: str
    ) -> Tuple[float, Optional[str]]:
        """
        Pixel-level comparison using PIL.

        Returns:
            (difference_percentage, diff_image_path or None)
        """
        baseline_img = Image.open(io.BytesIO(baseline_data)).convert("RGB")
        current_img = Image.open(io.BytesIO(current_data)).convert("RGB")

        # Resize current to match baseline if dimensions differ
        if baseline_img.size != current_img.size:
            current_img = current_img.resize(baseline_img.size, Image.LANCZOS)

        # Compute absolute difference per pixel
        diff_img = ImageChops.difference(baseline_img, current_img)

        # Calculate percentage of different pixels
        diff_percent = self._calculate_diff_percentage(diff_img, baseline_img.size)

        # Generate diff visualisation when there's a meaningful change
        diff_image_path = None
        if diff_percent > 0.01:
            diff_image_path = self._generate_diff_image(
                baseline_img, current_img, diff_img, page_name
            )

        return diff_percent, diff_image_path

    def _byte_compare(self, baseline_data: bytes, current_data: bytes) -> float:
        """Simple byte-level comparison fallback (no PIL)."""
        min_len = min(len(baseline_data), len(current_data))
        if min_len == 0:
            return 100.0
        different_bytes = sum(
            1 for i in range(min_len)
            if baseline_data[i] != current_data[i]
        )
        return (different_bytes / min_len) * 100

    def _calculate_diff_percentage(
        self,
        diff_img: 'Image.Image',
        size: Tuple[int, int]
    ) -> float:
        """Calculate percentage of different pixels from the diff image."""
        gray_diff = diff_img.convert('L')
        histogram = gray_diff.histogram()

        # Pixels at intensity 0 are identical; everything else is different
        different_pixels = sum(histogram[1:])
        total_pixels = size[0] * size[1]

        return (different_pixels / total_pixels * 100) if total_pixels > 0 else 0.0

    def _generate_diff_image(
        self,
        baseline: 'Image.Image',
        current: 'Image.Image',
        diff: 'Image.Image',
        page_name: str
    ) -> str:
        """Generate side-by-side comparison image with diff highlights."""
        try:
            width, height = baseline.size
            padding = 10
            label_height = 40
            combined_width = width * 3 + padding * 4
            combined_height = height + label_height + padding * 2

            combined = Image.new('RGB', (combined_width, combined_height), 'white')

            # Paste images side by side
            y_offset = label_height + padding
            combined.paste(baseline, (padding, y_offset))
            combined.paste(current, (width + padding * 2, y_offset))

            # Create a highlighted diff (differences shown in red)
            diff_highlighted = current.copy()
            diff_mask = diff.convert('L')
            red_overlay = Image.new('RGB', current.size, (255, 0, 0))
            diff_highlighted = Image.composite(red_overlay, diff_highlighted, diff_mask)
            combined.paste(diff_highlighted, (width * 2 + padding * 3, y_offset))

            # Add labels
            draw = ImageDraw.Draw(combined)
            try:
                font = ImageFont.truetype("arial.ttf", 18)
            except (IOError, OSError):
                font = ImageFont.load_default()

            draw.text((padding + width // 2 - 40, 10), "BASELINE", fill='black', font=font)
            draw.text((width + padding * 2 + width // 2 - 35, 10), "CURRENT", fill='black', font=font)
            draw.text((width * 2 + padding * 3 + width // 2 - 55, 10), "DIFFERENCES", fill='red', font=font)

            # Save
            safe_name = page_name.replace('/', '_').replace(':', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            diff_filename = f"diff_{safe_name}_{timestamp}.png"
            diff_path = self.baseline_dir / diff_filename
            combined.save(diff_path)

            return str(diff_path)

        except Exception as e:
            return f"Error generating diff image: {e}"

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all comparisons"""
        if not self.results:
            return {"status": "no_comparisons", "total": 0}

        passed = sum(1 for r in self.results if r.get("passed"))
        failed = sum(1 for r in self.results if not r.get("passed"))

        significant_changes = [
            {
                "page_name": r["page_name"],
                "diff_percentage": r["difference_percentage"],
                "passed": r["passed"]
            }
            for r in self.results
            if r.get("is_significant_change")
        ]

        return {
            "status": "complete",
            "total_comparisons": len(self.results),
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / len(self.results) * 100, 1) if self.results else 0,
            "threshold_used": round(self.threshold * 100, 2),
            "significant_changes": significant_changes
        }

    def export_report(self, output_path: str = "visual_regression_report.json") -> str:
        """Export detailed comparison report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "details": self.results
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        return output_path
