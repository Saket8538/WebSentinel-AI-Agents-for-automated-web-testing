"""
Enhanced PDF Report Generator with Charts, Detailed Analysis, and AI Insights
Creates comprehensive, professional-grade PDF reports with visualizations
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
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics import renderPDF
from reportlab.lib.colors import HexColor
from PIL import Image as PILImage
from urllib.parse import urlparse


class EnhancedPDFReportGenerator:
    """Generate comprehensive, detailed PDF reports with charts and AI insights"""
    
    def __init__(self, results: Dict[str, Any], screenshots_dir: str = None, ai_insights: str = None):
        self.results = results
        self.screenshots_dir = Path(screenshots_dir) if screenshots_dir else None
        self.ai_insights = ai_insights
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.page_count = 0
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Main Title
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=HexColor('#1a1a2e'),
            spaceAfter=20,
            spaceBefore=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=34
        ))
        
        # Subtitle
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=HexColor('#16213e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=18
        ))
        
        # Section Header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=HexColor('#0f3460'),
            spaceAfter=15,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            borderWidth=2,
            borderColor=HexColor('#e94560'),
            borderPadding=5,
            backColor=HexColor('#f5f5f5')
        ))
        
        # Subsection Header
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=HexColor('#16213e'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold',
            leading=18
        ))
        
        # Info Box
        self.styles.add(ParagraphStyle(
            name='InfoBox',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#333333'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica',
            backColor=HexColor('#e8f4f8'),
            borderWidth=1,
            borderColor=HexColor('#3498db'),
            borderPadding=10,
            leading=14
        ))
        
        # Warning Box
        self.styles.add(ParagraphStyle(
            name='WarningBox',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#856404'),
            backColor=HexColor('#fff3cd'),
            borderWidth=1,
            borderColor=HexColor('#ffc107'),
            borderPadding=10,
            leading=14
        ))
        
        # Error Box
        self.styles.add(ParagraphStyle(
            name='ErrorBox',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#721c24'),
            backColor=HexColor('#f8d7da'),
            borderWidth=1,
            borderColor=HexColor('#dc3545'),
            borderPadding=10,
            leading=14
        ))
        
        # Code Style
        self.styles.add(ParagraphStyle(
            name='CodeStyle',
            parent=self.styles['Code'],
            fontSize=9,
            textColor=HexColor('#2d2d2d'),
            backColor=HexColor('#f4f4f4'),
            fontName='Courier',
            leftIndent=20,
            rightIndent=20,
            borderWidth=1,
            borderColor=HexColor('#cccccc'),
            borderPadding=10,
            leading=12
        ))
        
        # Metric Style
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=24,
            textColor=HexColor('#0f3460'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=5
        ))
        
        # Metric Label
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#666666'),
            fontName='Helvetica',
            alignment=TA_CENTER,
            spaceAfter=15
        ))
        
        # Status styles with enhanced formatting
        status_styles = {
            'PASS': ('#27ae60', '#d5f4e6'),
            'FAIL': ('#e74c3c', '#fadbd8'),
            'WARNING': ('#f39c12', '#fcf3cf'),
            'CRITICAL': ('#c0392b', '#f2d7d5')
        }
        
        for status, (text_color, bg_color) in status_styles.items():
            self.styles.add(ParagraphStyle(
                name=f'Status{status}',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=HexColor(text_color),
                backColor=HexColor(bg_color),
                fontName='Helvetica-Bold',
                borderWidth=1,
                borderColor=HexColor(text_color),
                borderPadding=5,
                leading=15
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

    def _calculate_health_score(self) -> int:
        """Calculate overall health score (0-100)"""
        tests = self.results.get('tests', {})
        if not tests:
            return 0
        
        weights = {
            'page_load': 20,
            'security': 25,
            'accessibility': 20,
            'links': 10,
            'forms': 10,
            'responsive': 10,
            'console_errors': 5
        }
        
        total_score = 0
        total_weight = 0
        
        for test_name, weight in weights.items():
            if test_name in tests:
                status = tests[test_name].get('status', 'FAIL')
                if status == 'PASS':
                    total_score += weight
                elif status == 'WARNING':
                    total_score += weight * 0.5
                total_weight += weight
        
        return int((total_score / total_weight * 100)) if total_weight > 0 else 0
    
    def _get_performance_grade(self, load_time: float) -> str:
        """Get performance grade based on load time"""
        if load_time < 1.0:
            return 'A+'
        elif load_time < 2.0:
            return 'A'
        elif load_time < 3.0:
            return 'B'
        elif load_time < 4.0:
            return 'C'
        elif load_time < 5.0:
            return 'D'
        else:
            return 'F'
    
    def _create_cover_page(self) -> List:
        """Create an attractive cover page"""
        elements = []
        
        # Title
        title = Paragraph("🌐 WebSentinel", self.styles['MainTitle'])
        elements.append(Spacer(1, 0.5*inch))
        elements.append(title)
        
        subtitle = Paragraph("Comprehensive Web Testing Report", self.styles['Subtitle'])
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3*inch))
        
        # URL Box
        url = self.results.get('url', 'N/A')
        url_text = f"<b>Tested URL:</b><br/>{url}"
        elements.append(Paragraph(url_text, self.styles['InfoBox']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Health Score - Large and prominent
        health_score = self._calculate_health_score()
        score_color = self._get_score_color(health_score)
        
        score_para = Paragraph(
            f'<font size="48" color="{score_color}"><b>{health_score}</b></font>',
            self.styles['MetricValue']
        )
        elements.append(score_para)
        
        score_label = Paragraph("Overall Health Score", self.styles['MetricLabel'])
        elements.append(score_label)
        elements.append(Spacer(1, 0.4*inch))
        
        # Quick Stats Table
        tests = self.results.get('tests', {})
        status_counts = {'PASS': 0, 'FAIL': 0, 'WARNING': 0}
        for test in tests.values():
            status = test.get('status', 'FAIL')
            if status in status_counts:
                status_counts[status] += 1
        
        stats_data = [
            ['Metric', 'Value'],
            ['Tests Passed', f"{status_counts['PASS']}"],
            ['Tests Failed', f"{status_counts['FAIL']}"],
            ['Warnings', f"{status_counts['WARNING']}"],
            ['Total Tests', f"{len(tests)}"],
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0f3460')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f5f5f5')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#cccccc')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f9f9f9')]),
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Timestamp
        timestamp = self.results.get('timestamp', datetime.now().isoformat())
        timestamp_text = f"<i>Report Generated: {timestamp}</i>"
        elements.append(Paragraph(timestamp_text, self.styles['Normal']))
        
        elements.append(PageBreak())
        return elements
    
    def _get_score_color(self, score: int) -> str:
        """Get color based on score"""
        if score >= 90:
            return '#27ae60'  # Green
        elif score >= 70:
            return '#f39c12'  # Orange
        else:
            return '#e74c3c'  # Red
    
    def _create_executive_summary(self) -> List:
        """Create detailed executive summary with charts"""
        elements = []
        
        elements.append(Paragraph("📊 Executive Summary", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Performance Overview
        tests = self.results.get('tests', {})
        page_load = tests.get('page_load', {})
        load_time = page_load.get('load_time', 0)
        perf_grade = self._get_performance_grade(load_time)
        
        overview_text = f"""
        <b>Performance Grade:</b> {perf_grade}<br/>
        <b>Load Time:</b> {load_time:.2f}s<br/>
        <b>Status Code:</b> {page_load.get('status_code', 'N/A')}<br/>
        <b>Health Score:</b> {self._calculate_health_score()}/100
        """
        elements.append(Paragraph(overview_text, self.styles['InfoBox']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Test Results Pie Chart
        status_counts = {'PASS': 0, 'FAIL': 0, 'WARNING': 0}
        for test in tests.values():
            status = test.get('status', 'FAIL')
            if status in status_counts:
                status_counts[status] += 1
        
        if sum(status_counts.values()) > 0:
            chart = self._create_pie_chart(status_counts)
            elements.append(chart)
            elements.append(Spacer(1, 0.3*inch))
        
        # Critical Issues Summary
        critical_issues = self._identify_critical_issues(tests)
        if critical_issues:
            elements.append(Paragraph("🚨 Critical Issues Requiring Immediate Attention", 
                                    self.styles['SubsectionHeader']))
            for issue in critical_issues[:5]:  # Top 5
                elements.append(Paragraph(f"• {issue}", self.styles['ErrorBox']))
                elements.append(Spacer(1, 0.1*inch))
        
        elements.append(PageBreak())
        return elements

    def _create_test_scope_section(self) -> List:
        """Create a section describing what was actually tested from prompt and logs."""
        elements = []

        task_description = (self.results.get('task_description') or '').strip()
        agent_logs = self.results.get('agent_logs', []) or []

        if not task_description and not agent_logs:
            return elements

        elements.append(Paragraph("🎯 Tested Scope & Prompt", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2 * inch))

        if task_description:
            safe_task = self._sanitize_text(task_description)
            elements.append(Paragraph(f"<b>User Prompt:</b> {safe_task}", self.styles['InfoBox']))
            elements.append(Spacer(1, 0.15 * inch))

        if agent_logs:
            elements.append(Paragraph("What the agent/tester actually did", self.styles['SubsectionHeader']))
            for line in agent_logs[-12:]:
                safe_line = self._sanitize_text(str(line))
                if safe_line:
                    elements.append(Paragraph(f"• {safe_line}", self.styles['Normal']))
                    elements.append(Spacer(1, 0.05 * inch))

        elements.append(Spacer(1, 0.2 * inch))
        return elements
    
    def _create_pie_chart(self, data: Dict[str, int]) -> Drawing:
        """Create a pie chart for test results"""
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 150
        pie.y = 50
        pie.width = 100
        pie.height = 100
        
        pie.data = [data['PASS'], data['FAIL'], data['WARNING']]
        pie.labels = [f"Pass ({data['PASS']})", f"Fail ({data['FAIL']})", f"Warning ({data['WARNING']})"]
        pie.slices.strokeWidth = 0.5
        pie.slices[0].fillColor = HexColor('#27ae60')
        pie.slices[1].fillColor = HexColor('#e74c3c')
        pie.slices[2].fillColor = HexColor('#f39c12')
        
        drawing.add(pie)
        return drawing
    
    def _identify_critical_issues(self, tests: Dict) -> List[str]:
        """Identify critical issues from test results"""
        critical = []
        
        # Page load issues
        page_load = tests.get('page_load', {})
        if page_load.get('load_time', 0) > 5:
            critical.append("Page load time exceeds 5 seconds - Users expect pages to load in under 3 seconds")
        
        if page_load.get('status_code', 200) >= 400:
            critical.append(f"HTTP error {page_load.get('status_code')} - Page is not accessible")
        
        # Security issues
        security = tests.get('security', {})
        missing_headers = security.get('missing_headers', [])
        if 'Content-Security-Policy' in missing_headers:
            critical.append("Missing Content-Security-Policy header - Site vulnerable to XSS attacks")
        if 'Strict-Transport-Security' in missing_headers:
            critical.append("Missing HSTS header - Site vulnerable to man-in-the-middle attacks")
        
        # Accessibility issues
        accessibility = tests.get('accessibility', {})
        issues = accessibility.get('issues', [])
        issue_count = len(issues) if isinstance(issues, list) else (issues if isinstance(issues, int) else 0)
        if issue_count > 10:
            critical.append(f"{issue_count} accessibility issues found - May violate WCAG guidelines")
        
        # Broken links
        links = tests.get('links', {})
        broken = links.get('broken_links', [])
        if len(broken) > 5:
            critical.append(f"{len(broken)} broken links found - Negatively impacts SEO and user experience")
        
        # Console errors
        console = tests.get('console_errors', {})
        errors = console.get('errors', [])
        if isinstance(errors, list):
            error_count = len(errors)
        else:
            error_count = errors if isinstance(errors, int) else 0
        if error_count > 0:
            critical.append(f"{error_count} JavaScript errors detected - May cause functionality issues")
        
        return critical
    
    def _create_detailed_performance_analysis(self) -> List:
        """Create detailed performance analysis section"""
        elements = []
        
        elements.append(Paragraph("⚡ Performance Deep Dive", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        page_load = self.results.get('tests', {}).get('page_load', {})
        load_time = page_load.get('load_time', 0)
        
        # Performance metrics table
        perf_data = [
            ['Metric', 'Value', 'Target', 'Status'],
            ['Load Time', f"{load_time:.2f}s", '< 3s', '✓' if load_time < 3 else '✗'],
            ['HTTP Status', str(page_load.get('status_code', 'N/A')), '200', '✓' if page_load.get('status_code') == 200 else '✗'],
            ['Performance Grade', self._get_performance_grade(load_time), 'A', '✓' if load_time < 2 else '✗'],
        ]
        
        perf_table = Table(perf_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0f3460')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f9f9f9')]),
        ]))
        
        elements.append(perf_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Performance recommendations
        elements.append(Paragraph("💡 Performance Optimization Recommendations", self.styles['SubsectionHeader']))
        
        recommendations = []
        if load_time > 3:
            recommendations.append(
                "• <b>Reduce server response time:</b> Optimize backend processing, use caching, upgrade hosting"
            )
            recommendations.append(
                "• <b>Optimize images:</b> Compress images, use WebP format, implement lazy loading"
            )
            recommendations.append(
                "• <b>Minify resources:</b> Minify CSS, JavaScript, and HTML files"
            )
            recommendations.append(
                "• <b>Enable compression:</b> Use Gzip or Brotli compression for text files"
            )
            recommendations.append(
                "• <b>Leverage browser caching:</b> Set appropriate cache headers for static resources"
            )
        else:
            recommendations.append("• ✓ Excellent performance! Maintain current optimization strategies")
        
        for rec in recommendations:
            elements.append(Paragraph(rec, self.styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _create_detailed_security_analysis(self) -> List:
        """Create detailed security analysis section"""
        elements = []
        
        elements.append(Paragraph("🔒 Security Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        security = self.results.get('tests', {}).get('security', {})
        headers = security.get('headers', {})
        present_headers = [k for k, v in headers.items() if v]
        missing_headers = security.get('missing_headers', [])
        
        # Security score
        total_headers = len(present_headers) + len(missing_headers)
        security_score = int((len(present_headers) / total_headers * 100)) if total_headers > 0 else 0
        
        score_text = f"<b>Security Score:</b> {security_score}/100"
        elements.append(Paragraph(score_text, self.styles['InfoBox']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Present headers
        if present_headers:
            elements.append(Paragraph("✓ Implemented Security Headers", self.styles['SubsectionHeader']))
            for header in present_headers:
                elements.append(Paragraph(f"• <b>{header}:</b> Configured correctly", self.styles['Normal']))
                elements.append(Spacer(1, 0.05*inch))
            elements.append(Spacer(1, 0.2*inch))
        
        # Missing headers with detailed explanations
        if missing_headers:
            elements.append(Paragraph("⚠️ Missing Security Headers", self.styles['SubsectionHeader']))
            
            header_explanations = {
                'Content-Security-Policy': (
                    'Prevents XSS attacks by controlling which resources can be loaded. '
                    'Add: Content-Security-Policy: default-src \'self\''
                ),
                'Strict-Transport-Security': (
                    'Forces HTTPS connections. '
                    'Add: Strict-Transport-Security: max-age=31536000; includeSubDomains'
                ),
                'X-Frame-Options': (
                    'Prevents clickjacking attacks. '
                    'Add: X-Frame-Options: DENY'
                ),
                'X-Content-Type-Options': (
                    'Prevents MIME-type sniffing. '
                    'Add: X-Content-Type-Options: nosniff'
                ),
                'Referrer-Policy': (
                    'Controls referrer information. '
                    'Add: Referrer-Policy: strict-origin-when-cross-origin'
                )
            }
            
            for header in missing_headers:
                explanation = header_explanations.get(header, 'Security header not configured')
                elements.append(Paragraph(f"<b>{header}</b>", self.styles['Normal']))
                elements.append(Paragraph(f"<i>{explanation}</i>", self.styles['WarningBox']))
                elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _create_detailed_accessibility_analysis(self) -> List:
        """Create detailed accessibility analysis section"""
        elements = []
        
        elements.append(Paragraph("♿ Accessibility Analysis (WCAG 2.1)", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        accessibility = self.results.get('tests', {}).get('accessibility', {})
        
        # WCAG Compliance Level
        issues_raw = accessibility.get('issues', [])
        issues_count = len(issues_raw) if isinstance(issues_raw, list) else int(issues_raw or 0)
        if issues_count == 0:
            compliance = "Level AAA"
            compliance_color = '#27ae60'
        elif issues_count < 5:
            compliance = "Level AA (Partial)"
            compliance_color = '#f39c12'
        else:
            compliance = "Level A (Partial)"
            compliance_color = '#e74c3c'
        
        compliance_text = f'<font color="{compliance_color}"><b>WCAG Compliance:</b> {compliance}</font>'
        elements.append(Paragraph(compliance_text, self.styles['InfoBox']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Detailed findings
        elements.append(Paragraph("Detailed Findings", self.styles['SubsectionHeader']))
        
        findings = [
            ("Missing alt text", accessibility.get('missing_alt', 0)),
            ("Missing form labels", accessibility.get('missing_labels', 0)),
            ("Improper heading structure", accessibility.get('heading_issues', 0)),
            ("Low color contrast", accessibility.get('contrast_issues', 0)),
            ("Missing ARIA landmarks", accessibility.get('missing_aria', 0))
        ]
        
        findings_data = [['Issue Type', 'Count', 'Severity']]
        for finding, count in findings:
            if count > 0:
                severity = 'High' if count > 10 else 'Medium' if count > 5 else 'Low'
                findings_data.append([finding, str(count), severity])
        
        if len(findings_data) > 1:
            findings_table = Table(findings_data, colWidths=[3*inch, 1*inch, 1.5*inch])
            findings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0f3460')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#cccccc')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f9f9f9')]),
            ]))
            elements.append(findings_table)
        else:
            elements.append(Paragraph("✓ No accessibility issues detected!", self.styles['InfoBox']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Fix examples
        if issues_count > 0:
            elements.append(Paragraph("🛠️ How to Fix", self.styles['SubsectionHeader']))
            fix_examples = [
                "<b>Alt Text:</b> Add descriptive alt attributes to all images: &lt;img src='photo.jpg' alt='Person smiling'&gt;",
                "<b>Form Labels:</b> Associate labels with inputs: &lt;label for='email'&gt;Email:&lt;/label&gt;&lt;input id='email'&gt;",
                "<b>Heading Structure:</b> Use proper heading hierarchy (H1, H2, H3) without skipping levels",
                "<b>Color Contrast:</b> Ensure text has at least 4.5:1 contrast ratio with background",
                "<b>ARIA Landmarks:</b> Add role attributes: &lt;nav role='navigation'&gt;&lt;/nav&gt;"
            ]
            
            for example in fix_examples:
                elements.append(Paragraph(f"• {example}", self.styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _create_ai_insights_section(self) -> List:
        """Create AI-powered insights section"""
        elements = []
        
        if not self.ai_insights:
            return elements
        
        elements.append(PageBreak())
        elements.append(Paragraph("🤖 AI-Powered Insights & Recommendations", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        intro = """
        Our AI has analyzed your test results and generated the following insights and recommendations:
        """
        elements.append(Paragraph(intro, self.styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Split AI insights into paragraphs
        insights_paragraphs = self.ai_insights.split('\n\n')
        for para in insights_paragraphs:
            if para.strip():
                safe_text = self._sanitize_text(para.strip())
                if safe_text:
                    elements.append(Paragraph(safe_text, self.styles['InfoBox']))
                    elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _create_action_plan(self) -> List:
        """Create prioritized action plan"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("📋 Prioritized Action Plan", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        tests = self.results.get('tests', {})
        
        # Categorize actions by priority
        critical_actions = []
        high_priority = []
        medium_priority = []
        low_priority = []
        
        # Analyze each test for actions
        page_load = tests.get('page_load', {})
        if page_load.get('load_time', 0) > 5:
            critical_actions.append(("Optimize page load time", "< 1 hour", "Performance", "Critical user experience issue"))
        elif page_load.get('load_time', 0) > 3:
            high_priority.append(("Improve page load time", "2-4 hours", "Performance", "User experience optimization"))
        
        security = tests.get('security', {})
        for header in security.get('missing_headers', []):
            if header in ['Content-Security-Policy', 'Strict-Transport-Security']:
                critical_actions.append((f"Add {header}", "30 minutes", "Security", "Prevents security vulnerabilities"))
            else:
                high_priority.append((f"Add {header}", "15 minutes", "Security", "Enhances security posture"))
        
        accessibility = tests.get('accessibility', {})
        issues = accessibility.get('issues', [])
        issue_count = len(issues) if isinstance(issues, list) else (issues if isinstance(issues, int) else 0)
        if issue_count > 10:
            high_priority.append(("Fix accessibility issues", "4-8 hours", "Accessibility", "WCAG compliance required"))
        elif issue_count > 0:
            medium_priority.append(("Address accessibility concerns", "2-4 hours", "Accessibility", "Improve user experience"))
        
        links = tests.get('links', {})
        if len(links.get('broken_links', [])) > 0:
            high_priority.append(("Fix broken links", "1-2 hours", "Content", "Improves SEO and UX"))
        
        # Create action tables
        if critical_actions:
            elements.append(Paragraph("🚨 Critical (Do Immediately)", self.styles['SubsectionHeader']))
            self._add_action_table(elements, critical_actions)
            elements.append(Spacer(1, 0.2*inch))
        
        if high_priority:
            elements.append(Paragraph("⚠️ High Priority (This Week)", self.styles['SubsectionHeader']))
            self._add_action_table(elements, high_priority)
            elements.append(Spacer(1, 0.2*inch))
        
        if medium_priority:
            elements.append(Paragraph("📌 Medium Priority (This Month)", self.styles['SubsectionHeader']))
            self._add_action_table(elements, medium_priority)
            elements.append(Spacer(1, 0.2*inch))
        
        if not critical_actions and not high_priority and not medium_priority:
            elements.append(Paragraph("✓ No critical issues found! Your site is in great shape.", 
                                    self.styles['InfoBox']))
        
        return elements
    
    def _add_action_table(self, elements: List, actions: List):
        """Add action items table"""
        data = [['Action', 'Effort', 'Category', 'Impact']]
        for action in actions:
            data.append(list(action))
        
        table = Table(data, colWidths=[2.5*inch, 1*inch, 1*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0f3460')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f9f9f9')]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(table)
    
    def _add_enhanced_screenshots(self) -> List:
        """Add screenshots with descriptions and annotations"""
        elements = []
        
        if not self.screenshots_dir or not self.screenshots_dir.exists():
            return elements
        
        screenshot_files = sorted(self.screenshots_dir.glob("*.png"))
        
        if not screenshot_files:
            return elements
        
        elements.append(PageBreak())
        elements.append(Paragraph("📸 Visual Evidence & Screenshots", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        for idx, screenshot in enumerate(screenshot_files[:10], 1):  # Max 10 screenshots
            try:
                # Add page break every 2 screenshots
                if idx > 1 and idx % 2 == 1:
                    elements.append(PageBreak())
                
                # Resize image to fit page
                img = PILImage.open(screenshot)
                img_width, img_height = img.size
                
                # Calculate aspect ratio
                max_width = 6.5 * inch
                max_height = 3.5 * inch
                
                ratio = min(max_width / img_width, max_height / img_height)
                new_width = img_width * ratio
                new_height = img_height * ratio
                
                elements.append(Paragraph(f"<b>Step {idx}:</b> {screenshot.stem.replace('_', ' ').title()}", 
                                        self.styles['SubsectionHeader']))
                elements.append(Spacer(1, 0.1*inch))
                
                img_element = Image(str(screenshot), width=new_width, height=new_height)
                elements.append(img_element)
                elements.append(Spacer(1, 0.3*inch))
                
            except Exception as e:
                elements.append(Paragraph(f"Error loading screenshot: {e}", self.styles['Normal']))
        
        return elements
    
    def generate(self, output_path: str = None) -> str:
        """Generate the enhanced PDF report"""
        if output_path is None:
            # Generate filename
            safe_url = urlparse(self.results.get('url', 'test')).netloc
            safe_url = safe_url.replace('.', '_').replace(':', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"enhanced_report_{safe_url}_{timestamp}.pdf"
        
        # Convert to Path and handle if already includes directory
        output_path = Path(output_path)
        
        # If output_path is absolute or already includes reports dir, use it directly
        if output_path.is_absolute() or 'reports' in str(output_path.parent):
            full_path = output_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # Ensure reports directory exists
            reports_dir = Path('reports')
            reports_dir.mkdir(exist_ok=True)
            full_path = reports_dir / output_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create PDF
        doc = SimpleDocTemplate(
            str(full_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            title=f"WebSentinel Report - {self.results.get('url', 'N/A')}",
            author="WebSentinel AI Testing Platform"
        )
        
        # Build content
        elements = []
        elements.extend(self._create_cover_page())
        elements.extend(self._create_test_scope_section())
        elements.extend(self._create_executive_summary())
        elements.extend(self._create_detailed_performance_analysis())
        elements.extend(self._create_detailed_security_analysis())
        elements.extend(self._create_detailed_accessibility_analysis())
        elements.extend(self._create_ai_insights_section())
        elements.extend(self._create_action_plan())
        elements.extend(self._add_enhanced_screenshots())
        
        # Build PDF
        doc.build(elements)
        
        print(f"✓ Enhanced PDF report generated: {full_path}")
        return str(full_path)
