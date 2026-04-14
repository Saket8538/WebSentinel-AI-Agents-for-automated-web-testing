"""
AI-Powered Accessibility Analyzer
WCAG 2.1 Level AA/AAA compliance checker with AI recommendations
Includes real contrast ratio checking against WCAG luminance formulas.
"""
import re
import math
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime


# ──────────────────────────────────────────────────────────────
# CSS Named Colors (subset covering the most common ones)
# ──────────────────────────────────────────────────────────────
_NAMED_COLORS = {
    "black": (0, 0, 0), "white": (255, 255, 255), "red": (255, 0, 0),
    "green": (0, 128, 0), "blue": (0, 0, 255), "yellow": (255, 255, 0),
    "cyan": (0, 255, 255), "magenta": (255, 0, 255), "gray": (128, 128, 128),
    "grey": (128, 128, 128), "silver": (192, 192, 192), "maroon": (128, 0, 0),
    "olive": (128, 128, 0), "lime": (0, 255, 0), "aqua": (0, 255, 255),
    "teal": (0, 128, 128), "navy": (0, 0, 128), "fuchsia": (255, 0, 255),
    "purple": (128, 0, 128), "orange": (255, 165, 0), "pink": (255, 192, 203),
    "brown": (165, 42, 42), "coral": (255, 127, 80), "crimson": (220, 20, 60),
    "darkgray": (169, 169, 169), "darkgrey": (169, 169, 169),
    "darkred": (139, 0, 0), "darkgreen": (0, 100, 0), "darkblue": (0, 0, 139),
    "lightgray": (211, 211, 211), "lightgrey": (211, 211, 211),
    "lightblue": (173, 216, 230), "lightgreen": (144, 238, 144),
    "transparent": (0, 0, 0),  # treated as black for contrast purposes
}


class ContrastChecker:
    """
    WCAG 2.1 contrast-ratio calculator.

    Implements the sRGB relative-luminance formula and contrast-ratio
    thresholds defined in WCAG 2.1 Success Criteria 1.4.3 (AA) and 1.4.6 (AAA).

    Can be used standalone:
        checker = ContrastChecker()
        ratio = checker.contrast_ratio((255, 255, 255), (0, 0, 0))
        # => 21.0
    """

    # WCAG thresholds
    AA_NORMAL_TEXT = 4.5
    AA_LARGE_TEXT = 3.0
    AAA_NORMAL_TEXT = 7.0
    AAA_LARGE_TEXT = 4.5

    @staticmethod
    def _linearize(channel: int) -> float:
        """Convert an 8-bit sRGB channel value to linear RGB."""
        c = channel / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    @classmethod
    def relative_luminance(cls, rgb: Tuple[int, int, int]) -> float:
        """WCAG relative luminance (0.0 – 1.0)."""
        r, g, b = rgb
        return (
            0.2126 * cls._linearize(r)
            + 0.7152 * cls._linearize(g)
            + 0.0722 * cls._linearize(b)
        )

    @classmethod
    def contrast_ratio(
        cls,
        fg: Tuple[int, int, int],
        bg: Tuple[int, int, int],
    ) -> float:
        """
        Return the WCAG contrast ratio between two sRGB colours.
        The result is always >= 1.0 (higher = more contrast).
        """
        l1 = cls.relative_luminance(fg)
        l2 = cls.relative_luminance(bg)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)

    @classmethod
    def passes_aa(cls, fg: Tuple[int, int, int], bg: Tuple[int, int, int], large_text: bool = False) -> bool:
        threshold = cls.AA_LARGE_TEXT if large_text else cls.AA_NORMAL_TEXT
        return cls.contrast_ratio(fg, bg) >= threshold

    @classmethod
    def passes_aaa(cls, fg: Tuple[int, int, int], bg: Tuple[int, int, int], large_text: bool = False) -> bool:
        threshold = cls.AAA_LARGE_TEXT if large_text else cls.AAA_NORMAL_TEXT
        return cls.contrast_ratio(fg, bg) >= threshold

    # ── colour parsing helpers ────────────────────────────────

    @staticmethod
    def parse_color(color_str: str) -> Optional[Tuple[int, int, int]]:
        """
        Parse a CSS colour value into (R, G, B).
        Supports: #RGB, #RRGGBB, rgb(r,g,b), rgba(r,g,b,a), named colours.
        Returns None if the string cannot be parsed.
        """
        if not color_str:
            return None
        s = color_str.strip().lower()

        # Named colour
        if s in _NAMED_COLORS:
            return _NAMED_COLORS[s]

        # #RGB or #RRGGBB
        hex_match = re.match(r'^#([0-9a-f]{3,8})$', s)
        if hex_match:
            h = hex_match.group(1)
            if len(h) == 3:
                return (int(h[0]*2, 16), int(h[1]*2, 16), int(h[2]*2, 16))
            if len(h) >= 6:
                return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

        # rgb(r, g, b) / rgba(r, g, b, a)
        rgb_match = re.match(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', s)
        if rgb_match:
            return (
                min(int(rgb_match.group(1)), 255),
                min(int(rgb_match.group(2)), 255),
                min(int(rgb_match.group(3)), 255),
            )

        return None

    @classmethod
    def extract_color_pairs(cls, page_content: str) -> List[Dict[str, Any]]:
        """
        Scan HTML/CSS for inline style declarations that set both
        ``color`` and ``background-color`` (or ``background``) on
        the same element.  Returns a list of dicts with parsed
        foreground/background pairs.
        """
        pairs: List[Dict[str, Any]] = []

        # Match style="..." blocks
        style_blocks = re.findall(r'style\s*=\s*["\']([^"\']+)["\']', page_content, re.IGNORECASE)

        for block in style_blocks:
            fg_match = re.search(r'(?:^|;)\s*color\s*:\s*([^;]+)', block, re.IGNORECASE)
            bg_match = re.search(r'(?:^|;)\s*background(?:-color)?\s*:\s*([^;]+)', block, re.IGNORECASE)

            if fg_match and bg_match:
                fg = cls.parse_color(fg_match.group(1).strip())
                bg = cls.parse_color(bg_match.group(1).strip())
                if fg and bg:
                    ratio = cls.contrast_ratio(fg, bg)
                    pairs.append({
                        "foreground": fg_match.group(1).strip(),
                        "background": bg_match.group(1).strip(),
                        "fg_rgb": fg,
                        "bg_rgb": bg,
                        "contrast_ratio": round(ratio, 2),
                        "passes_aa_normal": ratio >= cls.AA_NORMAL_TEXT,
                        "passes_aa_large": ratio >= cls.AA_LARGE_TEXT,
                        "passes_aaa_normal": ratio >= cls.AAA_NORMAL_TEXT,
                    })

        return pairs


class AccessibilityAnalyzer:
    """Comprehensive WCAG 2.1 accessibility analysis"""
    
    def __init__(self):
        self.wcag_level = "AA"  # Can be A, AA, or AAA
        self.issues = []
        self.contrast_checker = ContrastChecker()
        
    async def analyze_accessibility(
        self,
        page_content: str,
        page_title: str,
        images: List[Dict[str, Any]],
        forms: List[Dict[str, Any]],
        headings: List[str]
    ) -> Dict[str, Any]:
        """
        Comprehensive accessibility analysis
        
        Args:
            page_content: HTML content
            page_title: Page title
            images: List of images found
            forms: List of forms found
            headings: List of headings (h1-h6)
            
        Returns:
            Accessibility analysis results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "wcag_level": self.wcag_level,
            "compliance_score": 100,
            "issues": [],
            "contrast_results": [],
            "recommendations": [],
            "affected_users": []
        }
        
        # 1. Perceivable (WCAG Principle 1)
        perceivable_issues = self._check_perceivable(page_content, images, page_title)
        results["issues"].extend(perceivable_issues)
        
        # 1b. Real Contrast Ratio Analysis
        contrast_issues, contrast_details = self._check_contrast_ratios(page_content)
        results["issues"].extend(contrast_issues)
        results["contrast_results"] = contrast_details
        
        # 2. Operable (WCAG Principle 2)
        operable_issues = self._check_operable(forms, page_content)
        results["issues"].extend(operable_issues)
        
        # 3. Understandable (WCAG Principle 3)
        understandable_issues = self._check_understandable(page_content, headings, forms)
        results["issues"].extend(understandable_issues)
        
        # 4. Robust (WCAG Principle 4)
        robust_issues = self._check_robust(page_content)
        results["issues"].extend(robust_issues)
        
        # Calculate compliance score
        results["compliance_score"] = self._calculate_compliance_score(results["issues"])
        
        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results["issues"])
        
        # Identify affected user groups
        results["affected_users"] = self._identify_affected_users(results["issues"])
        
        return results
    
    def _check_perceivable(
        self, 
        page_content: str,
        images: List[Dict[str, Any]],
        page_title: str
    ) -> List[Dict[str, Any]]:
        """Check WCAG Principle 1: Perceivable"""
        issues = []
        
        # 1.1.1 Non-text Content (Level A)
        images_without_alt = [img for img in images if not img.get('alt')]
        if images_without_alt:
            issues.append({
                "wcag_sc": "1.1.1",
                "level": "A",
                "principle": "Perceivable",
                "guideline": "Text Alternatives",
                "issue": f"{len(images_without_alt)} images missing alt text",
                "impact": "Screen reader users cannot understand image content",
                "severity": "HIGH",
                "affected_groups": ["Blind users", "Screen reader users"],
                "fix": "Add descriptive alt attributes to all images: <img src='image.jpg' alt='Description'>",
                "code_example": "<img src='logo.png' alt='Company Logo'>"
            })
        
        # 1.3.1 Info and Relationships (Level A)
        if not re.search(r'<h1[^>]*>', page_content, re.IGNORECASE):
            issues.append({
                "wcag_sc": "1.3.1",
                "level": "A",
                "principle": "Perceivable",
                "guideline": "Adaptable",
                "issue": "No H1 heading found",
                "impact": "Page structure unclear to assistive technologies",
                "severity": "MEDIUM",
                "affected_groups": ["Screen reader users", "Cognitive disability users"],
                "fix": "Add a single H1 heading as main page title",
                "code_example": "<h1>Main Page Title</h1>"
            })
        
        # 1.4.1 Use of Color (Level A)
        color_keywords = ['red', 'green', 'blue', 'error', 'success', 'warning']
        color_usage = sum(page_content.lower().count(word) for word in color_keywords)
        if color_usage > 5:
            issues.append({
                "wcag_sc": "1.4.1",
                "level": "A",
                "principle": "Perceivable",
                "guideline": "Distinguishable",
                "issue": "Possible reliance on color alone for information",
                "impact": "Color-blind users may miss important information",
                "severity": "MEDIUM",
                "affected_groups": ["Color-blind users", "Low vision users"],
                "fix": "Use text, icons, or patterns in addition to color",
                "code_example": "<span class='error-icon'>⚠️</span> Error message"
            })
        
        # 2.4.2 Page Titled (Level A)
        if not page_title or len(page_title.strip()) < 3:
            issues.append({
                "wcag_sc": "2.4.2",
                "level": "A",
                "principle": "Operable",
                "guideline": "Navigable",
                "issue": "Page title missing or too short",
                "impact": "Users cannot identify page purpose",
                "severity": "HIGH",
                "affected_groups": ["All users", "Screen reader users"],
                "fix": "Add descriptive page title",
                "code_example": "<title>Home - Company Name</title>"
            })
        
        return issues

    def _check_contrast_ratios(self, page_content: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Real WCAG 1.4.3 contrast-ratio checking.
        Parses inline styles from the page HTML, computes contrast ratios,
        and reports failures.

        Returns:
            (issues_list, contrast_details_list)
        """
        issues: List[Dict[str, Any]] = []
        pairs = self.contrast_checker.extract_color_pairs(page_content)

        failing_pairs = [p for p in pairs if not p["passes_aa_normal"]]

        if failing_pairs:
            sample = failing_pairs[0]
            issues.append({
                "wcag_sc": "1.4.3",
                "level": "AA",
                "principle": "Perceivable",
                "guideline": "Distinguishable",
                "issue": (
                    f"{len(failing_pairs)} color pair(s) fail WCAG AA contrast ratio (4.5:1). "
                    f"Worst: {sample['foreground']} on {sample['background']} = {sample['contrast_ratio']}:1"
                ),
                "impact": "Low contrast text is difficult or impossible to read for low-vision users",
                "severity": "HIGH",
                "affected_groups": ["Low vision users", "Elderly users"],
                "fix": "Ensure contrast ratio of at least 4.5:1 for normal text, 3:1 for large text",
                "code_example": f"Change '{sample['foreground']}' on '{sample['background']}' to meet 4.5:1 ratio"
            })
        elif not pairs:
            # No inline color pairs found — note that external CSS is not checked
            issues.append({
                "wcag_sc": "1.4.3",
                "level": "AA",
                "principle": "Perceivable",
                "guideline": "Distinguishable",
                "issue": "No inline color pairs found to check; external CSS contrast should be verified separately",
                "impact": "Low contrast text difficult to read",
                "severity": "LOW",
                "affected_groups": ["Low vision users", "Elderly users"],
                "fix": "Ensure contrast ratio of at least 4.5:1 for normal text, 3:1 for large text",
                "code_example": "Use tools like WebAIM Contrast Checker for external stylesheets"
            })
        # else: all inline pairs pass — no issue appended

        return issues, pairs
    
    def _check_operable(self, forms: List[Dict[str, Any]], page_content: str) -> List[Dict[str, Any]]:
        """Check WCAG Principle 2: Operable"""
        issues = []
        
        # 2.1.1 Keyboard (Level A)
        if 'onkeydown' in page_content.lower() or 'onkeypress' in page_content.lower():
            issues.append({
                "wcag_sc": "2.1.1",
                "level": "A",
                "principle": "Operable",
                "guideline": "Keyboard Accessible",
                "issue": "Potential keyboard trap detected",
                "impact": "Keyboard users may get stuck",
                "severity": "HIGH",
                "affected_groups": ["Keyboard-only users", "Motor disability users"],
                "fix": "Ensure all functionality is keyboard accessible and no keyboard traps exist",
                "code_example": "Test with Tab, Shift+Tab, Enter, Escape keys"
            })
        
        # 3.2.2 On Input (Level A)
        for form in forms:
            inputs_without_labels = 0
            for inp in form.get('inputs', []):
                if not inp.get('label') and not inp.get('aria-label'):
                    inputs_without_labels += 1
            
            if inputs_without_labels > 0:
                issues.append({
                    "wcag_sc": "3.2.2",
                    "level": "A",
                    "principle": "Understandable",
                    "guideline": "Predictable",
                    "issue": f"{inputs_without_labels} form inputs without labels",
                    "impact": "Users cannot identify input purpose",
                    "severity": "HIGH",
                    "affected_groups": ["Screen reader users", "Cognitive disability users"],
                    "fix": "Add <label> elements or aria-label attributes to all inputs",
                    "code_example": "<label for='email'>Email:</label><input id='email' type='email'>"
                })
                break
        
        # 2.4.7 Focus Visible (Level AA)
        if ':focus' not in page_content and 'outline' not in page_content:
            issues.append({
                "wcag_sc": "2.4.7",
                "level": "AA",
                "principle": "Operable",
                "guideline": "Navigable",
                "issue": "No visible focus indicators detected",
                "impact": "Keyboard users cannot see which element has focus",
                "severity": "MEDIUM",
                "affected_groups": ["Keyboard-only users", "Motor disability users"],
                "fix": "Ensure focusable elements have visible focus indicators",
                "code_example": "button:focus { outline: 2px solid blue; }"
            })
        
        return issues
    
    def _check_understandable(
        self,
        page_content: str,
        headings: List[str],
        forms: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check WCAG Principle 3: Understandable"""
        issues = []
        
        # 3.1.1 Language of Page (Level A)
        if not re.search(r'<html[^>]*\slang=', page_content, re.IGNORECASE):
            issues.append({
                "wcag_sc": "3.1.1",
                "level": "A",
                "principle": "Understandable",
                "guideline": "Readable",
                "issue": "Page language not specified",
                "impact": "Screen readers cannot pronounce text correctly",
                "severity": "MEDIUM",
                "affected_groups": ["Screen reader users", "International users"],
                "fix": "Add lang attribute to <html> tag",
                "code_example": "<html lang='en'>"
            })
        
        # 3.3.1 Error Identification (Level A)
        has_error_handling = any(
            'error' in str(form).lower() or 'invalid' in str(form).lower()
            for form in forms
        )
        if forms and not has_error_handling:
            issues.append({
                "wcag_sc": "3.3.1",
                "level": "A",
                "principle": "Understandable",
                "guideline": "Input Assistance",
                "issue": "Forms lack error identification",
                "impact": "Users cannot identify and correct input errors",
                "severity": "MEDIUM",
                "affected_groups": ["All users", "Cognitive disability users"],
                "fix": "Provide clear error messages for invalid inputs",
                "code_example": "<span role='alert' class='error'>Email is required</span>"
            })
        
        # 3.3.2 Labels or Instructions (Level A)
        for form in forms:
            if not any('required' in str(inp).lower() for inp in form.get('inputs', [])):
                issues.append({
                    "wcag_sc": "3.3.2",
                    "level": "A",
                    "principle": "Understandable",
                    "guideline": "Input Assistance",
                    "issue": "Form fields missing required field indicators",
                    "impact": "Users don't know which fields are mandatory",
                    "severity": "LOW",
                    "affected_groups": ["All users", "Cognitive disability users"],
                    "fix": "Mark required fields clearly",
                    "code_example": "<label>Email <span aria-label='required'>*</span></label>"
                })
                break
        
        return issues
    
    def _check_robust(self, page_content: str) -> List[Dict[str, Any]]:
        """Check WCAG Principle 4: Robust"""
        issues = []
        
        # 4.1.1 Parsing (Level A)
        parsing_errors = []
        
        id_pattern = r'id=["\']([^"\']+)["\']'
        ids = re.findall(id_pattern, page_content)
        duplicate_ids = [id for id in ids if ids.count(id) > 1]
        if duplicate_ids:
            parsing_errors.append(f"Duplicate IDs: {set(duplicate_ids)}")
        
        open_tags = len(re.findall(r'<(?!/)(\\w+)', page_content))
        close_tags = len(re.findall(r'</(\\w+)>', page_content))
        if abs(open_tags - close_tags) > 5:
            parsing_errors.append("Possible unclosed HTML tags")
        
        if parsing_errors:
            issues.append({
                "wcag_sc": "4.1.1",
                "level": "A",
                "principle": "Robust",
                "guideline": "Compatible",
                "issue": f"HTML parsing issues: {', '.join(parsing_errors)}",
                "impact": "Assistive technologies may not parse content correctly",
                "severity": "HIGH",
                "affected_groups": ["Screen reader users", "All assistive technology users"],
                "fix": "Validate HTML and fix parsing errors",
                "code_example": "Use W3C HTML Validator"
            })
        
        # 4.1.2 Name, Role, Value (Level A)
        has_aria = 'aria-' in page_content.lower()
        if not has_aria:
            issues.append({
                "wcag_sc": "4.1.2",
                "level": "A",
                "principle": "Robust",
                "guideline": "Compatible",
                "issue": "No ARIA attributes detected",
                "impact": "Custom UI components may not be accessible",
                "severity": "LOW",
                "affected_groups": ["Screen reader users", "Assistive technology users"],
                "fix": "Add ARIA attributes to custom components",
                "code_example": "<button aria-label='Close dialog' aria-pressed='false'>"
            })
        
        return issues
    
    def _calculate_compliance_score(self, issues: List[Dict[str, Any]]) -> int:
        """Calculate WCAG compliance score (0-100)"""
        if not issues:
            return 100
        
        severity_deductions = {
            'HIGH': 15,
            'MEDIUM': 8,
            'LOW': 3
        }
        
        score = 100
        for issue in issues:
            severity = issue.get('severity', 'LOW')
            score -= severity_deductions.get(severity, 5)
        
        return max(0, score)
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate prioritized recommendations"""
        if not issues:
            return ["✅ No accessibility issues found! Great job!"]
        
        high = [i for i in issues if i.get('severity') == 'HIGH']
        medium = [i for i in issues if i.get('severity') == 'MEDIUM']
        low = [i for i in issues if i.get('severity') == 'LOW']
        
        recommendations = []
        
        if high:
            recommendations.append(f"🚨 URGENT: Fix {len(high)} high-severity issues first")
            for issue in high[:3]:
                recommendations.append(f"  • {issue['issue']}: {issue['fix']}")
        
        if medium:
            recommendations.append(f"⚠️ IMPORTANT: Address {len(medium)} medium-severity issues")
            for issue in medium[:2]:
                recommendations.append(f"  • {issue['issue']}: {issue['fix']}")
        
        if low:
            recommendations.append(f"ℹ️ NICE TO HAVE: Consider {len(low)} low-severity improvements")
        
        return recommendations
    
    def _identify_affected_users(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Identify user groups affected by accessibility issues"""
        affected = set()
        for issue in issues:
            affected.update(issue.get('affected_groups', []))
        return sorted(list(affected))
