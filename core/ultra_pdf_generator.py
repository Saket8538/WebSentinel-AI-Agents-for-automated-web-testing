"""
Ultra-Enhanced PDF Report Generator - Comprehensive 25+ Page Reports
Generates detailed, professional PDF reports with AI insights, guidance, and actionable recommendations
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor
from urllib.parse import urlparse

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class UltraEnhancedPDFGenerator:
    """Generate comprehensive 25+ page PDF reports with detailed analysis and guidance"""
    
    def __init__(
        self,
        results: Dict[str, Any],
        screenshots_dir: str = None,
        ai_insights: str = None,
        security_results: Dict = None,
        accessibility_results: Dict = None,
        performance_results: Dict = None,
        seo_results: Dict = None
    ):
        self.results = results
        self.screenshots_dir = Path(screenshots_dir) if screenshots_dir else None
        self.ai_insights = ai_insights
        self.security_results = security_results or {}
        self.accessibility_results = accessibility_results or {}
        self.performance_results = performance_results or {}
        self.seo_results = seo_results or {}
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup comprehensive custom styles"""
        # Main Title
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=32,
            textColor=HexColor('#1a1a2e'),
            spaceAfter=25,
            spaceBefore=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=40
        ))
        
        # Subtitle
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=HexColor('#16213e'),
            spaceAfter=35,
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=22
        ))
        
        # Section Header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=20,
            textColor=HexColor('#0f3460'),
            spaceAfter=18,
            spaceBefore=25,
            fontName='Helvetica-Bold',
            backColor=HexColor('#f0f4f8'),
            leading=26
        ))
        
        # Subsection Header
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=HexColor('#16213e'),
            spaceAfter=12,
            spaceBefore=18,
            fontName='Helvetica-Bold',
            leading=20
        ))
        
        # Custom Body Text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#333333'),
            spaceAfter=8,
            spaceBefore=4,
            fontName='Helvetica',
            leading=16,
            alignment=TA_JUSTIFY
        ))
        
        # Info Box - Blue
        self.styles.add(ParagraphStyle(
            name='InfoBox',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#0c5460'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica',
            backColor=HexColor('#d1ecf1'),
            borderPadding=12,
            leading=16
        ))
        
        # Success Box - Green
        self.styles.add(ParagraphStyle(
            name='SuccessBox',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#155724'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica',
            backColor=HexColor('#d4edda'),
            borderPadding=12,
            leading=16
        ))
        
        # Warning Box - Yellow
        self.styles.add(ParagraphStyle(
            name='WarningBox',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#856404'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica',
            backColor=HexColor('#fff3cd'),
            borderPadding=12,
            leading=16
        ))
        
        # Error Box - Red
        self.styles.add(ParagraphStyle(
            name='ErrorBox',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#721c24'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica',
            backColor=HexColor('#f8d7da'),
            borderPadding=12,
            leading=16
        ))
        
        # Code Style
        self.styles.add(ParagraphStyle(
            name='CodeStyle',
            parent=self.styles['Code'],
            fontSize=9,
            textColor=HexColor('#2d2d2d'),
            backColor=HexColor('#f4f4f4'),
            fontName='Courier',
            leftIndent=15,
            rightIndent=15,
            borderPadding=10,
            leading=14,
            spaceAfter=10,
            spaceBefore=10
        ))
        
        # Tip Box
        self.styles.add(ParagraphStyle(
            name='TipBox',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#004085'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica',
            backColor=HexColor('#cce5ff'),
            borderPadding=12,
            leading=16
        ))
        
        # Metric Value
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=36,
            textColor=HexColor('#0f3460'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=5
        ))
        
        # Metric Label
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#666666'),
            fontName='Helvetica',
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        # Bullet Point
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#333333'),
            spaceAfter=6,
            spaceBefore=2,
            fontName='Helvetica',
            leading=16,
            leftIndent=20,
            bulletIndent=10
        ))
    
    @staticmethod
    def _sanitize_text(text: str) -> str:
        """Sanitize text for ReportLab Paragraph (which uses XML parser).
        Escapes HTML/XML special chars and strips unsupported markup."""
        import re as _re
        if not text:
            return ''
        # Replace XML special chars
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        # Strip markdown bold/italic markers
        text = _re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = _re.sub(r'\*(.+?)\*', r'\1', text)
        # Strip markdown code blocks
        text = _re.sub(r'```[\s\S]*?```', '[code block omitted]', text)
        text = _re.sub(r'`([^`]+)`', r'\1', text)
        # Strip markdown links
        text = _re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # Strip markdown headers
        text = _re.sub(r'^#{1,6}\s+', '', text, flags=_re.MULTILINE)
        return text

    @staticmethod
    def _as_list(value: Any) -> List[Any]:
        """Normalize a value into a list for safe iteration."""
        if isinstance(value, list):
            return value
        if value is None:
            return []
        return [value]

    def _collect_issue_fix_items(self) -> List[Dict[str, str]]:
        """Collect issue/fix pairs from all available result sources."""
        items: List[Dict[str, str]] = []
        tests = self.results.get('tests', {})

        # Security headers from comprehensive tests
        for header in tests.get('security', {}).get('missing_headers', []):
            items.append({
                'category': 'Security',
                'severity': 'HIGH' if header in ['Content-Security-Policy', 'Strict-Transport-Security'] else 'MEDIUM',
                'issue': f'Missing security header: {header}',
                'fix': f'Configure {header} in server/application response headers.'
            })

        # Broken links
        for link in tests.get('links', {}).get('broken_links', [])[:10]:
            items.append({
                'category': 'Reliability',
                'severity': 'MEDIUM',
                'issue': f"Broken link: {link.get('url', 'unknown')}",
                'fix': 'Update or remove the broken URL and ensure endpoint returns HTTP 200/301.'
            })

        # Console errors
        for err in self._as_list(tests.get('console_errors', {}).get('errors', []))[:10]:
            items.append({
                'category': 'JavaScript',
                'severity': 'HIGH',
                'issue': f"Console error: {str(err)[:120]}",
                'fix': 'Reproduce in browser devtools, then fix the failing script/module and add regression tests.'
            })

        # Accessibility issues from advanced analyzer
        for issue in self.accessibility_results.get('issues', [])[:20]:
            items.append({
                'category': 'Accessibility',
                'severity': issue.get('severity', 'MEDIUM'),
                'issue': issue.get('issue', 'Accessibility issue found'),
                'fix': issue.get('fix', 'Apply WCAG-compliant HTML semantics and ARIA where required.')
            })

        # Security vulnerabilities from advanced scanner
        for vuln in self.security_results.get('vulnerabilities', [])[:20]:
            items.append({
                'category': 'Security',
                'severity': vuln.get('severity', 'MEDIUM'),
                'issue': vuln.get('finding', 'Security finding detected'),
                'fix': vuln.get('fix', 'Apply the recommended security remediation and verify with retest.')
            })

        # Performance bottlenecks
        for bottleneck in self.performance_results.get('bottlenecks', [])[:20]:
            items.append({
                'category': 'Performance',
                'severity': bottleneck.get('severity', 'MEDIUM'),
                'issue': bottleneck.get('type', 'Performance bottleneck detected'),
                'fix': bottleneck.get('impact', 'Optimize render path, assets, and server response times.')
            })

        return items

    def _group_actions_by_priority(self, actions: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
        """Group actions into critical/high/medium buckets."""
        grouped = {'critical': [], 'high': [], 'medium': []}
        for action in actions:
            sev = str(action.get('severity', 'MEDIUM')).upper()
            if sev in ['CRITICAL', 'HIGH']:
                target = 'critical' if sev == 'CRITICAL' else 'high'
            else:
                target = 'medium'
            grouped[target].append(action)
        return grouped

    def _calculate_overall_score(self) -> int:
        """Calculate comprehensive overall score"""
        scores = []
        weights = []
        
        if self.performance_results:
            perf_score = self.performance_results.get('performance_score', 50)
            scores.append(perf_score)
            weights.append(25)
        
        if self.security_results:
            sec_score = self.security_results.get('security_score', 50)
            scores.append(sec_score)
            weights.append(25)
        
        if self.accessibility_results:
            acc_score = self.accessibility_results.get('compliance_score', 50)
            scores.append(acc_score)
            weights.append(20)
        
        tests = self.results.get('tests', {})
        if tests:
            passed = sum(1 for t in tests.values() if t.get('status') == 'PASS')
            total = len(tests)
            test_score = int((passed / total * 100)) if total > 0 else 50
            scores.append(test_score)
            weights.append(30)
        
        if not scores:
            return 50
        
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        total_weight = sum(weights)
        return int(weighted_sum / total_weight)
    
    def _get_grade(self, score: int) -> tuple:
        """Get letter grade and color based on score"""
        if score >= 90:
            return 'A+', '#27ae60', 'Excellent'
        elif score >= 80:
            return 'A', '#2ecc71', 'Very Good'
        elif score >= 70:
            return 'B', '#f39c12', 'Good'
        elif score >= 60:
            return 'C', '#e67e22', 'Fair'
        elif score >= 50:
            return 'D', '#e74c3c', 'Needs Improvement'
        else:
            return 'F', '#c0392b', 'Critical Issues'
    
    def _get_table_style(self) -> TableStyle:
        """Get standard table style"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0f3460')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#dee2e6')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f8f9fa')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
    
    def _get_critical_issues(self) -> List[str]:
        """Extract critical issues from all results"""
        critical = []
        
        if self.security_results:
            vulns = self.security_results.get('vulnerabilities', [])
            for v in vulns:
                if v.get('severity') == 'HIGH':
                    critical.append(f"Security: {v.get('finding', 'High severity vulnerability')}")
        
        if self.performance_results:
            bottlenecks = self.performance_results.get('bottlenecks', [])
            for b in bottlenecks:
                if b.get('severity') == 'HIGH':
                    critical.append(f"Performance: {b.get('type', 'Performance issue')}")
        
        if self.accessibility_results:
            issues = self.accessibility_results.get('issues', [])
            for i in issues:
                if i.get('severity') == 'HIGH':
                    critical.append(f"Accessibility: {i.get('issue', 'High severity issue')}")
        
        return critical
    
    def _get_quick_wins(self) -> List[str]:
        """Get quick wins that are easy to implement"""
        wins = []
        
        if self.security_results:
            vulns = self.security_results.get('vulnerabilities', [])
            for v in vulns:
                if v.get('severity') in ['LOW', 'MEDIUM']:
                    fix = v.get('fix', '')
                    if fix and len(fix) < 100:
                        wins.append(f"Security: {fix}")
        
        if self.accessibility_results:
            issues = self.accessibility_results.get('issues', [])
            for i in issues:
                if i.get('severity') == 'LOW':
                    wins.append(f"Accessibility: {i.get('fix', 'Fix issue')}")
        
        if not wins:
            wins = [
                "Enable browser caching for static assets",
                "Add meta description tags for better SEO",
                "Compress images using WebP format",
                "Minify CSS and JavaScript files",
                "Add alt text to all images"
            ]
        
        return wins[:5]
    
    def _create_cover_page(self) -> List:
        """Create professional cover page"""
        elements = []
        
        elements.append(Spacer(1, 1.5*inch))
        
        # Main Title
        elements.append(Paragraph("WebSentinel", self.styles['MainTitle']))
        elements.append(Paragraph("Comprehensive Web Testing Report", self.styles['Subtitle']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # URL & Goal Box
        url = self.results.get('url', 'N/A')
        task = self.results.get('task_description', '').strip()
        
        info_text = f"<b>Analyzed URL:</b> {url}"
        if task:
            info_text += f"<br/><br/><b>User Goal / Prompt:</b> {task}"
            
        elements.append(Paragraph(info_text, self.styles['InfoBox']))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Overall Score
        overall_score = self._calculate_overall_score()
        grade, color, description = self._get_grade(overall_score)
        
        score_text = f'<font size="60" color="{color}"><b>{overall_score}</b></font>'
        elements.append(Paragraph(score_text, self.styles['MetricValue']))
        elements.append(Paragraph(f"Overall Health Score | Grade: {grade} ({description})", self.styles['MetricLabel']))
        
        elements.append(Spacer(1, 0.4*inch))
        
        # Quick Overview Table
        overview_data = [['Category', 'Score', 'Status']]
        
        if self.performance_results:
            perf = self.performance_results.get('performance_score', 0)
            overview_data.append(['Performance', f'{perf}/100', self._get_grade(perf)[2]])
        
        if self.security_results:
            sec = self.security_results.get('security_score', 0)
            overview_data.append(['Security', f'{sec}/100', self._get_grade(sec)[2]])
        
        if self.accessibility_results:
            acc = self.accessibility_results.get('compliance_score', 0)
            overview_data.append(['Accessibility', f'{acc}/100', self._get_grade(acc)[2]])
        
        tests = self.results.get('tests', {})
        if tests:
            passed = sum(1 for t in tests.values() if t.get('status') == 'PASS')
            pct = f'{int(passed/len(tests)*100)}%' if tests else 'N/A'
            overview_data.append(['Tests Passed', f'{passed}/{len(tests)}', pct])
        
        if len(overview_data) > 1:
            table = Table(overview_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
            table.setStyle(self._get_table_style())
            elements.append(table)
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Report Info
        timestamp = self.results.get('timestamp', datetime.now().isoformat())
        info_text = f"<b>Report Generated:</b> {timestamp}<br/><b>Testing Platform:</b> WebSentinel AI<br/><b>Report Version:</b> 2.0 Ultra-Enhanced"
        elements.append(Paragraph(info_text, self.styles['CustomBody']))
        
        elements.append(PageBreak())
        return elements
    
    def _create_table_of_contents(self) -> List:
        """Create table of contents"""
        elements = []
        
        elements.append(Paragraph("Table of Contents", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        toc_items = [
            ("1. Executive Summary", "Overview of findings and key metrics"),
            ("2. Performance Analysis", "Page speed, load times, and optimization tips"),
            ("3. Security Assessment", "OWASP Top 10 vulnerabilities and fixes"),
            ("4. Accessibility Audit", "WCAG 2.1 compliance check"),
            ("5. SEO Analysis", "Search engine optimization review"),
            ("6. Test Results Detail", "Comprehensive test breakdown"),
            ("7. AI Agent Plain-English Analysis", "Narrative of the agent's actions and findings"),
            ("8. Step-by-Step Fix Guide", "How to resolve each issue"),
            ("9. Action Plan", "Prioritized roadmap for improvements"),
            ("10. Visual Evidence", "Screenshots and annotations"),
            ("11. Technical Appendix", "Detailed technical data"),
            ("12. Resources and References", "Helpful links and tools")
        ]
        
        for title, description in toc_items:
            elements.append(Paragraph(f"<b>{title}</b>", self.styles['CustomBody']))
            elements.append(Paragraph(f"<i>{description}</i>", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(PageBreak())
        return elements
    
    def _create_executive_summary(self) -> List:
        """Create detailed executive summary"""
        elements = []
        
        elements.append(Paragraph("1. Executive Summary", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Introduction
        url = self.results.get('url', 'the website')
        intro_text = f"This comprehensive report presents the results of an automated analysis of <b>{url}</b>. The assessment covers performance, security, accessibility, and SEO - providing actionable insights to improve your website's overall quality and user experience."
        elements.append(Paragraph(intro_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Key Findings Summary
        elements.append(Paragraph("Key Findings Overview", self.styles['SubsectionHeader']))
        
        findings = []
        
        if self.performance_results:
            perf_score = self.performance_results.get('performance_score', 0)
            if perf_score >= 70:
                findings.append(f"Performance: Good performance with a score of {perf_score}/100")
            else:
                findings.append(f"Performance: Needs optimization - score {perf_score}/100")
        
        if self.security_results:
            sec_score = self.security_results.get('security_score', 0)
            vulns = self.security_results.get('total_vulnerabilities', 0)
            if sec_score >= 70:
                findings.append(f"Security: Adequate security posture - score {sec_score}/100")
            else:
                findings.append(f"Security: {vulns} vulnerabilities found - score {sec_score}/100")
        
        if self.accessibility_results:
            acc_score = self.accessibility_results.get('compliance_score', 0)
            issues = len(self.accessibility_results.get('issues', []))
            if acc_score >= 70:
                findings.append(f"Accessibility: WCAG compliant - score {acc_score}/100")
            else:
                findings.append(f"Accessibility: {issues} issues found - score {acc_score}/100")
        
        tests = self.results.get('tests', {})
        if tests:
            passed = sum(1 for t in tests.values() if t.get('status') == 'PASS')
            failed = sum(1 for t in tests.values() if t.get('status') == 'FAIL')
            if failed == 0:
                findings.append(f"Tests: All {passed} tests passed successfully")
            else:
                findings.append(f"Tests: {failed} of {len(tests)} tests failed")
        
        for finding in findings:
            elements.append(Paragraph(f"* {finding}", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Critical Issues
        elements.append(Paragraph("Critical Issues Requiring Immediate Attention", self.styles['SubsectionHeader']))
        
        critical_issues = self._get_critical_issues()
        if critical_issues:
            for issue in critical_issues[:5]:
                elements.append(Paragraph(f"CRITICAL: {issue}", self.styles['ErrorBox']))
                elements.append(Spacer(1, 0.1*inch))
        else:
            elements.append(Paragraph("No critical issues detected! Your website is in good health.", self.styles['SuccessBox']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Quick Wins
        elements.append(Paragraph("Quick Wins - Easy Improvements", self.styles['SubsectionHeader']))
        
        quick_wins = self._get_quick_wins()
        for win in quick_wins:
            elements.append(Paragraph(f"TIP: {win}", self.styles['TipBox']))
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(PageBreak())
        return elements
    
    def _create_performance_section(self) -> List:
        """Create detailed performance analysis section"""
        elements = []
        
        elements.append(Paragraph("2. Performance Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        intro = "Website performance directly impacts user experience, conversion rates, and SEO rankings. Studies show that 53% of mobile users abandon sites that take longer than 3 seconds to load. This section analyzes your website's performance metrics and provides optimization recommendations."
        elements.append(Paragraph(intro, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        if self.performance_results:
            score = self.performance_results.get('performance_score', 0)
            grade, color, desc = self._get_grade(score)
            
            elements.append(Paragraph(f"Performance Score: <font color='{color}'><b>{score}/100 ({grade})</b></font>", self.styles['InfoBox']))
            elements.append(Spacer(1, 0.2*inch))
            
            # Metrics table
            elements.append(Paragraph("Current Performance Metrics", self.styles['SubsectionHeader']))
            
            current = self.performance_results.get('current_performance', {})
            if current:
                metrics_data = [['Metric', 'Value', 'Status', 'Benchmark']]
                for metric_name, metric_data in current.items():
                    value = metric_data.get('value', 'N/A')
                    status = metric_data.get('status', 'N/A')
                    benchmark = metric_data.get('benchmark', 'N/A')
                    metrics_data.append([metric_name.replace('_', ' ').title(), str(value), status, benchmark])
                
                metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 2.5*inch])
                metrics_table.setStyle(self._get_table_style())
                elements.append(metrics_table)
                elements.append(Spacer(1, 0.2*inch))
            
            # Bottlenecks
            bottlenecks = self.performance_results.get('bottlenecks', [])
            if bottlenecks:
                elements.append(Paragraph("Identified Bottlenecks", self.styles['SubsectionHeader']))
                for b in bottlenecks:
                    severity = b.get('severity', 'MEDIUM')
                    style = 'ErrorBox' if severity == 'HIGH' else 'WarningBox'
                    elements.append(Paragraph(
                        f"<b>{b.get('type', 'Issue')}</b><br/>Impact: {b.get('impact', 'Unknown')}<br/>Current: {b.get('value', 'N/A')} | Threshold: {b.get('threshold', 'N/A')}",
                        self.styles[style]
                    ))
                    elements.append(Spacer(1, 0.1*inch))
            
            # Recommendations
            recommendations = self.performance_results.get('optimization_recommendations', [])
            if recommendations:
                elements.append(Paragraph("Optimization Recommendations", self.styles['SubsectionHeader']))
                for rec in recommendations[:5]:
                    elements.append(Paragraph(f"<b>[{rec.get('priority', 'MEDIUM')}] {rec.get('title', 'Recommendation')}</b>", self.styles['CustomBody']))
                    elements.append(Paragraph(f"{rec.get('description', '')}", self.styles['CustomBody']))
                    
                    actions = rec.get('actions', [])
                    for action in actions[:3]:
                        elements.append(Paragraph(f"  * {action}", self.styles['BulletPoint']))
                    
                    elements.append(Paragraph(f"<i>Expected Improvement: {rec.get('expected_improvement', 'N/A')}</i>", self.styles['CustomBody']))
                    elements.append(Spacer(1, 0.15*inch))
        else:
            elements.append(Paragraph("Performance data not available. Run a performance analysis to see detailed metrics.", self.styles['InfoBox']))
        
        # Best Practices
        elements.append(PageBreak())
        elements.append(Paragraph("Performance Best Practices Guide", self.styles['SubsectionHeader']))
        
        best_practices = [
            ("<b>1. Optimize Images</b>", "Use WebP format, compress images, implement lazy loading. This alone can reduce page size by 40-60%."),
            ("<b>2. Enable Compression</b>", "Use Gzip or Brotli compression for text-based files (HTML, CSS, JS)."),
            ("<b>3. Leverage Browser Caching</b>", "Set appropriate Cache-Control headers. Static assets should be cached for at least 1 year."),
            ("<b>4. Minimize Render-Blocking Resources</b>", "Load CSS asynchronously, defer non-critical JavaScript."),
            ("<b>5. Use a CDN</b>", "Content Delivery Networks serve assets from servers closest to users."),
            ("<b>6. Optimize Fonts</b>", "Use font-display: swap, subset fonts, and limit font variations."),
            ("<b>7. Reduce Server Response Time</b>", "Optimize database queries, use caching, upgrade hosting if needed."),
        ]
        
        for title, desc in best_practices:
            elements.append(Paragraph(title, self.styles['CustomBody']))
            elements.append(Paragraph(desc, self.styles['CustomBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(PageBreak())
        return elements
    
    def _create_security_section(self) -> List:
        """Create detailed security analysis section"""
        elements = []
        
        elements.append(Paragraph("3. Security Assessment", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        intro = "Web security is critical for protecting your users and maintaining trust. This assessment evaluates your website against OWASP Top 10 vulnerabilities and common security misconfigurations."
        elements.append(Paragraph(intro, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        if self.security_results:
            score = self.security_results.get('security_score', 0)
            risk_level = self.security_results.get('risk_level', 'UNKNOWN')
            
            style = 'SuccessBox' if score >= 70 else 'WarningBox' if score >= 40 else 'ErrorBox'
            elements.append(Paragraph(
                f"Security Score: <b>{score}/100</b> | Risk Level: <b>{risk_level}</b>",
                self.styles[style]
            ))
            elements.append(Spacer(1, 0.2*inch))
            
            # Vulnerabilities
            vulns = self.security_results.get('vulnerabilities', [])
            total_vulns = self.security_results.get('total_vulnerabilities', len(vulns))
            
            elements.append(Paragraph(f"Vulnerabilities Found: {total_vulns}", self.styles['SubsectionHeader']))
            
            high_vulns = [v for v in vulns if v.get('severity') == 'HIGH']
            medium_vulns = [v for v in vulns if v.get('severity') == 'MEDIUM']
            low_vulns = [v for v in vulns if v.get('severity') == 'LOW']
            
            if high_vulns:
                elements.append(Paragraph("HIGH Severity Issues", self.styles['SubsectionHeader']))
                for v in high_vulns:
                    elements.append(Paragraph(
                        f"<b>{v.get('owasp_category', 'Security Issue')}</b><br/>Finding: {v.get('finding', 'N/A')}<br/>CVSS: {v.get('cvss_score', 'N/A')}<br/>Fix: {v.get('fix', 'N/A')}",
                        self.styles['ErrorBox']
                    ))
                    elements.append(Spacer(1, 0.1*inch))
            
            if medium_vulns:
                elements.append(Paragraph("MEDIUM Severity Issues", self.styles['SubsectionHeader']))
                for v in medium_vulns[:5]:
                    elements.append(Paragraph(
                        f"<b>{v.get('owasp_category', 'Security Issue')}</b>: {v.get('finding', 'N/A')}<br/>Fix: {v.get('fix', 'N/A')}",
                        self.styles['WarningBox']
                    ))
                    elements.append(Spacer(1, 0.1*inch))
            
            if low_vulns:
                elements.append(Paragraph(f"LOW Severity Issues: {len(low_vulns)} found", self.styles['InfoBox']))
        else:
            elements.append(Paragraph("Security scan data not available. Run a security scan for detailed results.", self.styles['InfoBox']))
        
        # Security Headers Guide
        elements.append(PageBreak())
        elements.append(Paragraph("Essential Security Headers Guide", self.styles['SubsectionHeader']))
        
        headers_guide = [
            ("Content-Security-Policy (CSP)", "Prevents XSS attacks by controlling which resources can be loaded."),
            ("Strict-Transport-Security (HSTS)", "Forces HTTPS connections, preventing man-in-the-middle attacks."),
            ("X-Frame-Options", "Prevents clickjacking by controlling frame embedding."),
            ("X-Content-Type-Options", "Prevents MIME type sniffing attacks."),
            ("X-XSS-Protection", "Enables browser XSS filtering."),
            ("Referrer-Policy", "Controls what referrer information is sent."),
        ]
        
        for header, desc in headers_guide:
            elements.append(Paragraph(f"<b>{header}</b>: {desc}", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(PageBreak())
        return elements
    
    def _create_accessibility_section(self) -> List:
        """Create detailed accessibility section"""
        elements = []
        
        elements.append(Paragraph("4. Accessibility Audit (WCAG 2.1)", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        intro = "Web accessibility ensures that websites are usable by people with disabilities. Following WCAG (Web Content Accessibility Guidelines) 2.1 is not only ethical but often legally required."
        elements.append(Paragraph(intro, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        if self.accessibility_results:
            score = self.accessibility_results.get('compliance_score', 0)
            wcag_level = self.accessibility_results.get('wcag_level', 'AA')
            
            style = 'SuccessBox' if score >= 70 else 'WarningBox' if score >= 40 else 'ErrorBox'
            elements.append(Paragraph(
                f"WCAG {wcag_level} Compliance Score: <b>{score}/100</b>",
                self.styles[style]
            ))
            elements.append(Spacer(1, 0.2*inch))
            
            issues = self.accessibility_results.get('issues', [])
            if issues:
                elements.append(Paragraph(f"Accessibility Issues Found: {len(issues)}", self.styles['SubsectionHeader']))
                
                issues_data = [['WCAG SC', 'Level', 'Issue', 'Severity']]
                for issue in issues[:10]:
                    issue_text = issue.get('issue', 'N/A')
                    if len(issue_text) > 40:
                        issue_text = issue_text[:40] + '...'
                    issues_data.append([
                        issue.get('wcag_sc', 'N/A'),
                        issue.get('level', 'N/A'),
                        issue_text,
                        issue.get('severity', 'N/A')
                    ])
                
                issues_table = Table(issues_data, colWidths=[0.8*inch, 0.6*inch, 3*inch, 0.8*inch])
                issues_table.setStyle(self._get_table_style())
                elements.append(issues_table)
                elements.append(Spacer(1, 0.2*inch))
                
                # Fixes
                elements.append(Paragraph("How to Fix These Issues", self.styles['SubsectionHeader']))
                for issue in issues[:5]:
                    elements.append(Paragraph(f"<b>{issue.get('issue', 'Issue')}</b>", self.styles['CustomBody']))
                    elements.append(Paragraph(f"Fix: {issue.get('fix', 'N/A')}", self.styles['TipBox']))
                    elements.append(Spacer(1, 0.1*inch))
            
            affected = self.accessibility_results.get('affected_users', [])
            if affected:
                elements.append(Paragraph("Users Affected by These Issues", self.styles['SubsectionHeader']))
                elements.append(Paragraph(", ".join(affected), self.styles['InfoBox']))
            
            recs = self.accessibility_results.get('recommendations', [])
            if recs:
                elements.append(Paragraph("Recommendations", self.styles['SubsectionHeader']))
                for rec in recs:
                    elements.append(Paragraph(f"* {rec}", self.styles['CustomBody']))
        else:
            elements.append(Paragraph("Accessibility data not available. Run an accessibility audit for detailed results.", self.styles['InfoBox']))
        
        elements.append(PageBreak())
        
        # WCAG Quick Reference
        elements.append(Paragraph("WCAG 2.1 Quick Reference Guide", self.styles['SubsectionHeader']))
        
        wcag_guide = [
            ("1. Perceivable", "Information must be presentable to users in ways they can perceive."),
            ("   - Text Alternatives", "Provide alt text for all non-text content"),
            ("   - Time-based Media", "Provide alternatives for audio/video content"),
            ("   - Adaptable", "Create content that can be presented in different ways"),
            ("2. Operable", "Interface components must be operable."),
            ("   - Keyboard Accessible", "All functionality available from keyboard"),
            ("   - Enough Time", "Give users enough time to read and use content"),
            ("   - Navigable", "Help users navigate and find content"),
            ("3. Understandable", "Information and operation must be understandable."),
            ("   - Readable", "Make text readable and understandable"),
            ("   - Predictable", "Make pages appear and operate predictably"),
            ("4. Robust", "Content must be robust enough for assistive technologies."),
            ("   - Compatible", "Maximize compatibility with assistive technologies"),
        ]
        
        for title, desc in wcag_guide:
            if title.startswith("   "):
                elements.append(Paragraph(f"{title}: {desc}", self.styles['BulletPoint']))
            else:
                elements.append(Paragraph(f"<b>{title}</b>: {desc}", self.styles['CustomBody']))
        
        elements.append(PageBreak())
        return elements
    
    def _create_seo_section(self) -> List:
        """Create SEO analysis section"""
        elements = []
        
        elements.append(Paragraph("5. SEO Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        intro = "Search Engine Optimization (SEO) determines how well your website ranks in search results. Good SEO practices improve visibility, drive organic traffic, and enhance credibility."
        elements.append(Paragraph(intro, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        if self.seo_results:
            for key, value in self.seo_results.items():
                elements.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", self.styles['CustomBody']))
        else:
            elements.append(Paragraph("SEO Best Practices Checklist", self.styles['SubsectionHeader']))
            
            checklist = [
                ("Title Tag", "Unique, descriptive, 50-60 characters"),
                ("Meta Description", "Compelling, includes keywords, 150-160 characters"),
                ("Header Tags", "Proper H1-H6 hierarchy, one H1 per page"),
                ("Image Alt Text", "Descriptive alt text for all images"),
                ("URL Structure", "Clean, readable URLs with keywords"),
                ("Mobile Friendly", "Responsive design, mobile-first approach"),
                ("Page Speed", "Fast loading times (under 3 seconds)"),
                ("Internal Links", "Logical internal linking structure"),
                ("SSL Certificate", "HTTPS enabled for security and SEO"),
                ("Sitemap", "XML sitemap submitted to search engines"),
            ]
            
            for item, desc in checklist:
                elements.append(Paragraph(f"<b>{item}:</b> {desc}", self.styles['BulletPoint']))
        
        elements.append(PageBreak())
        return elements
    
    def _create_test_results_section(self) -> List:
        """Create detailed test results section"""
        elements = []
        
        elements.append(Paragraph("6. Test Results Detail", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        tests = self.results.get('tests', {})
        
        if tests:
            results_data = [['Test', 'Status', 'Details']]
            
            for test_name, test_data in tests.items():
                status = test_data.get('status', 'N/A')
                details = str(test_data.get('load_time', test_data.get('issues', test_data.get('count', test_data.get('message', 'N/A')))))[:50]
                results_data.append([test_name.replace('_', ' ').title(), status, details])
            
            results_table = Table(results_data, colWidths=[2*inch, 1*inch, 3.5*inch])
            results_table.setStyle(self._get_table_style())
            elements.append(results_table)
            elements.append(Spacer(1, 0.3*inch))
            
            for test_name, test_data in tests.items():
                elements.append(Paragraph(f"<b>{test_name.replace('_', ' ').title()}</b>", self.styles['SubsectionHeader']))
                
                status = test_data.get('status', 'N/A')
                style = 'SuccessBox' if status == 'PASS' else 'WarningBox' if status == 'WARNING' else 'ErrorBox'
                
                details_text = f"Status: <b>{status}</b>"
                for key, value in test_data.items():
                    if key != 'status' and value:
                        details_text += f"<br/>{key.replace('_', ' ').title()}: {value}"
                
                elements.append(Paragraph(details_text, self.styles[style]))
                elements.append(Spacer(1, 0.15*inch))
        else:
            elements.append(Paragraph("No test results available.", self.styles['InfoBox']))
        
        elements.append(PageBreak())
        return elements
    
    def _create_ai_insights_section(self) -> List:
        """Create AI insights section"""
        elements = []
        
        elements.append(Paragraph("7. AI Agent Plain-English Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        intro = "Our AI Agent actually navigated your website to test the specific goals you set. Below is a plain-English narrative of exactly what was tested, what was found, and the biggest wins and concerns."
        elements.append(Paragraph(intro, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        if self.ai_insights:
            paragraphs = self.ai_insights.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    safe_text = self._sanitize_text(para.strip())
                    if not safe_text:
                        continue
                    if para.strip().startswith('#'):
                        elements.append(Paragraph(safe_text, self.styles['SubsectionHeader']))
                    else:
                        elements.append(Paragraph(safe_text, self.styles['InfoBox']))
                        elements.append(Spacer(1, 0.1*inch))
        else:
            task = (self.results.get('task_description') or '').strip()
            logs = self._as_list(self.results.get('agent_logs', []))
            elements.append(Paragraph("Agent Narrative From This Test Run", self.styles['SubsectionHeader']))

            if task:
                elements.append(Paragraph(f"<b>User Prompt:</b> {self._sanitize_text(task)}", self.styles['InfoBox']))
                elements.append(Spacer(1, 0.1 * inch))

            if logs:
                for line in logs[-15:]:
                    safe = self._sanitize_text(str(line))
                    if safe:
                        elements.append(Paragraph(f"• {safe}", self.styles['CustomBody']))
            else:
                elements.append(Paragraph(
                    "No explicit agent log entries were captured for this run. The analysis below is built from measured test outputs.",
                    self.styles['WarningBox']
                ))

            issue_items = self._collect_issue_fix_items()
            if issue_items:
                elements.append(Spacer(1, 0.15 * inch))
                elements.append(Paragraph("Top Findings From Actual Tests", self.styles['SubsectionHeader']))
                for item in issue_items[:6]:
                    issue = self._sanitize_text(item.get('issue', 'Issue detected'))
                    fix = self._sanitize_text(item.get('fix', 'Fix required'))
                    elements.append(Paragraph(f"<b>{issue}</b><br/>Fix: {fix}", self.styles['TipBox']))
                    elements.append(Spacer(1, 0.08 * inch))
        
        elements.append(PageBreak())
        return elements
    
    def _create_fix_guide_section(self) -> List:
        """Create step-by-step fix guide"""
        elements = []
        
        elements.append(Paragraph("8. Step-by-Step Fix Guide", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        intro = "This section provides detailed, step-by-step instructions for fixing the issues found in your website. Follow these guides in order of priority (Critical - High - Medium - Low)."
        elements.append(Paragraph(intro, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        issues = self._collect_issue_fix_items()
        if not issues:
            elements.append(Paragraph("No actionable issues were detected for this run.", self.styles['SuccessBox']))
            elements.append(PageBreak())
            return elements

        grouped = self._group_actions_by_priority(issues)
        section_order = [
            ('critical', 'Critical Fixes (first 24 hours)'),
            ('high', 'High Priority Fixes (this week)'),
            ('medium', 'Medium Priority Fixes (this month)')
        ]

        for key, title in section_order:
            entries = grouped.get(key, [])
            if not entries:
                continue
            elements.append(Paragraph(title, self.styles['SubsectionHeader']))
            for idx, entry in enumerate(entries[:8], 1):
                issue_text = self._sanitize_text(entry.get('issue', 'Issue detected'))
                fix_text = self._sanitize_text(entry.get('fix', 'Apply remediation and retest'))
                sev = self._sanitize_text(entry.get('severity', 'MEDIUM'))
                cat = self._sanitize_text(entry.get('category', 'General'))
                elements.append(Paragraph(
                    f"<b>{idx}. [{cat} | {sev}] {issue_text}</b><br/>"
                    f"<b>Fix Steps:</b> {fix_text}<br/>"
                    f"<b>Validation:</b> Re-run this specific test and verify status changes to PASS.",
                    self.styles['TipBox']
                ))
                elements.append(Spacer(1, 0.1 * inch))
        
        elements.append(PageBreak())
        return elements
    
    def _create_action_plan_section(self) -> List:
        """Create prioritized action plan"""
        elements = []
        
        elements.append(Paragraph("9. Prioritized Action Plan", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        intro = "Based on the analysis, here is your prioritized action plan. Address critical issues first, then work through high and medium priority items."
        elements.append(Paragraph(intro, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        issues = self._collect_issue_fix_items()
        grouped = self._group_actions_by_priority(issues)

        elements.append(Paragraph("Critical (Do Immediately)", self.styles['SubsectionHeader']))
        if grouped['critical']:
            for issue in grouped['critical'][:5]:
                text = self._sanitize_text(issue.get('issue', 'Critical issue'))
                elements.append(Paragraph(f"CRITICAL: {text}", self.styles['ErrorBox']))
                elements.append(Spacer(1, 0.05*inch))
        else:
            elements.append(Paragraph("No critical issues identified from this specific test run.", self.styles['SuccessBox']))

        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Recommended Timeline (Generated From Findings)", self.styles['SubsectionHeader']))

        timeline_data = [['Timeframe', 'Priority', 'Focus Area', 'Expected Impact']]
        if grouped['critical']:
            timeline_data.append(['Today', 'Critical', 'Security/Runtime errors', 'Remove immediate risk and outages'])
        if grouped['high']:
            timeline_data.append(['This Week', 'High', 'Performance and broken journeys', 'Improve UX and conversion'])
        if grouped['medium']:
            timeline_data.append(['This Month', 'Medium', 'Accessibility/SEO polish', 'Compliance and discoverability gains'])
        timeline_data.append(['Ongoing', 'Maintenance', 'Retesting and monitoring', 'Prevent regressions'])

        timeline_table = Table(timeline_data, colWidths=[1.2*inch, 1*inch, 2*inch, 2*inch])
        timeline_table.setStyle(self._get_table_style())
        elements.append(timeline_table)
        
        elements.append(PageBreak())
        return elements
    
    def _create_screenshots_section(self) -> List:
        """Create screenshots section"""
        elements = []
        
        if not self.screenshots_dir or not self.screenshots_dir.exists():
            return elements
        
        screenshots = list(self.screenshots_dir.glob("*.png"))
        if not screenshots:
            return elements
        
        elements.append(Paragraph("10. Visual Evidence", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        for i, screenshot in enumerate(screenshots[:8], 1):
            if PIL_AVAILABLE:
                try:
                    img = PILImage.open(screenshot)
                    w, h = img.size
                    max_w, max_h = 6*inch, 4*inch
                    ratio = min(max_w/w, max_h/h)
                    
                    elements.append(Paragraph(f"<b>Screenshot {i}:</b> {screenshot.stem}", self.styles['CustomBody']))
                    elements.append(Image(str(screenshot), width=w*ratio, height=h*ratio))
                    elements.append(Spacer(1, 0.2*inch))
                    
                    if i % 2 == 0:
                        elements.append(PageBreak())
                except Exception:
                    pass
        
        elements.append(PageBreak())
        return elements
    
    def _create_appendix(self) -> List:
        """Create technical appendix"""
        elements = []
        
        elements.append(Paragraph("11. Technical Appendix", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        elements.append(Paragraph("Raw Test Data", self.styles['SubsectionHeader']))
        
        data_text = json.dumps(self.results.get('tests', {}), indent=2, default=str)
        if len(data_text) > 2000:
            data_text = data_text[:2000] + "\n... (truncated)"
        safe_data_text = self._sanitize_text(data_text)
        elements.append(Paragraph(f"<font face='Courier' size='8'>{safe_data_text}</font>", self.styles['CodeStyle']))
        
        elements.append(PageBreak())
        return elements
    
    def _create_resources_section(self) -> List:
        """Create resources and references section"""
        elements = []
        
        elements.append(Paragraph("12. Resources and References", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        resources = [
            ("Performance Testing Tools", [
                "Google PageSpeed Insights: https://pagespeed.web.dev/",
                "GTmetrix: https://gtmetrix.com/",
                "WebPageTest: https://www.webpagetest.org/",
            ]),
            ("Security Resources", [
                "OWASP Top 10: https://owasp.org/Top10/",
                "Mozilla Observatory: https://observatory.mozilla.org/",
                "Security Headers: https://securityheaders.com/",
            ]),
            ("Accessibility Resources", [
                "WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/",
                "WAVE Tool: https://wave.webaim.org/",
                "axe DevTools: https://www.deque.com/axe/",
            ]),
            ("SEO Resources", [
                "Google Search Console: https://search.google.com/search-console",
                "Moz: https://moz.com/learn/seo",
                "Ahrefs Blog: https://ahrefs.com/blog/",
            ]),
        ]
        
        for category, links in resources:
            elements.append(Paragraph(f"<b>{category}</b>", self.styles['CustomBody']))
            for link in links:
                elements.append(Paragraph(f"  * {link}", self.styles['BulletPoint']))
            elements.append(Spacer(1, 0.15*inch))
        
        # Final Note
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(
            "Thank you for using WebSentinel! For questions or feedback, visit our documentation.",
            self.styles['InfoBox']
        ))
        
        return elements
    
    def generate(self, output_path: str = None) -> str:
        """Generate the ultra-enhanced PDF report"""
        if output_path is None:
            safe_url = urlparse(self.results.get('url', 'test')).netloc
            safe_url = safe_url.replace('.', '_').replace(':', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"ultra_report_{safe_url}_{timestamp}.pdf"
        
        output_path = Path(output_path)
        
        if not output_path.is_absolute():
            reports_dir = Path('reports')
            reports_dir.mkdir(exist_ok=True)
            output_path = reports_dir / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create PDF
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.6*inch,
            leftMargin=0.6*inch,
            topMargin=0.6*inch,
            bottomMargin=0.6*inch,
            title=f"WebSentinel Ultra Report - {self.results.get('url', 'N/A')}",
            author="WebSentinel AI Testing Platform"
        )
        
        # Build all sections
        elements = []
        elements.extend(self._create_cover_page())
        elements.extend(self._create_table_of_contents())
        elements.extend(self._create_executive_summary())
        elements.extend(self._create_performance_section())
        elements.extend(self._create_security_section())
        elements.extend(self._create_accessibility_section())
        elements.extend(self._create_seo_section())
        elements.extend(self._create_test_results_section())
        elements.extend(self._create_ai_insights_section())
        elements.extend(self._create_fix_guide_section())
        elements.extend(self._create_action_plan_section())
        elements.extend(self._create_screenshots_section())
        elements.extend(self._create_appendix())
        elements.extend(self._create_resources_section())
        
        # Build PDF
        doc.build(elements)
        
        print(f"Ultra-Enhanced PDF Report Generated: {output_path}")
        print(f"   Estimated Pages: 25+")
        return str(output_path)
