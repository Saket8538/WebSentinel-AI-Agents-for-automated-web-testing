"""
PDF Report Generator
Creates comprehensive PDF reports from web testing results with screenshots and metrics
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from urllib.parse import urlparse

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER
from PIL import Image as PILImage


class PDFReportGenerator:
    """Generate comprehensive PDF reports from test results"""
    
    def __init__(self, results: Dict[str, Any], screenshots_dir: str = None):
        self.results = results
        self.screenshots_dir = Path(screenshots_dir) if screenshots_dir else None
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section Header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#3498DB'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection Header
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#2980B9'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Status styles
        for status, color in [('PASS', '#27AE60'), ('FAIL', '#E74C3C'), ('WARNING', '#F39C12')]:
            self.styles.add(ParagraphStyle(
                name=f'Status{status}',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor(color),
                fontName='Helvetica-Bold'
            ))
    
    def _get_status_color(self, status: str) -> colors.Color:
        """Get color for status"""
        status_colors = {
            'PASS': colors.HexColor('#27AE60'),
            'FAIL': colors.HexColor('#E74C3C'),
            'WARNING': colors.HexColor('#F39C12')
        }
        return status_colors.get(status, colors.grey)
    
    def _create_header(self) -> List:
        """Create report header"""
        elements = []
        
        # Title
        title = Paragraph(
            f"Web Testing Report",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # URL and timestamp
        url = self.results.get('url', 'N/A')
        timestamp = self.results.get('timestamp', 'N/A')
        
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        info_data = [
            ['URL:', url],
            ['Test Date:', timestamp],
            ['Overall Status:', self.results.get('overall_status', 'N/A')]
        ]
        
        info_table = Table(info_data, colWidths=[1.5*inch, 5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (1, 2), (1, 2), self._get_status_color(self.results.get('overall_status', 'N/A'))),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.5*inch))

        task_description = (self.results.get('task_description') or '').strip()
        if task_description:
            elements.append(Paragraph(f"<b>Test Prompt:</b> {task_description}", self.styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))

        agent_logs = self.results.get('agent_logs', []) or []
        if agent_logs:
            elements.append(Paragraph("<b>What Was Tested (Agent/Test Logs):</b>", self.styles['Normal']))
            for line in agent_logs[-8:]:
                elements.append(Paragraph(f"• {str(line)}", self.styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_summary(self) -> List:
        """Create test summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        tests = self.results.get('tests', {})
        
        # Count statuses
        status_counts = {'PASS': 0, 'FAIL': 0, 'WARNING': 0}
        for test in tests.values():
            status = test.get('status', 'FAIL')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        summary_data = [
            ['Test Category', 'Status', 'Details'],
        ]
        
        test_names = {
            'page_load': 'Page Load Performance',
            'links': 'Link Validation',
            'forms': 'Form Analysis',
            'responsive': 'Responsive Design',
            'security': 'Security Headers',
            'accessibility': 'Accessibility',
            'console_errors': 'Console Errors'
        }
        
        for test_key, test_result in tests.items():
            status = test_result.get('status', 'FAIL')
            message = test_result.get('message', 'No details')
            
            summary_data.append([
                test_names.get(test_key, test_key.replace('_', ' ').title()),
                status,
                message
            ])
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1.2*inch, 3.3*inch])
        summary_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        # Add status colors
        for idx, (test_key, test_result) in enumerate(tests.items(), start=1):
            status = test_result.get('status', 'FAIL')
            color = self._get_status_color(status)
            summary_table.setStyle(TableStyle([
                ('TEXTCOLOR', (1, idx), (1, idx), color),
                ('FONTNAME', (1, idx), (1, idx), 'Helvetica-Bold'),
            ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Overall statistics
        total_tests = len(tests)
        pass_rate = (status_counts['PASS'] / total_tests * 100) if total_tests > 0 else 0
        
        stats_text = f"""
        <b>Test Statistics:</b><br/>
        • Total Tests: {total_tests}<br/>
        • Passed: {status_counts['PASS']}<br/>
        • Failed: {status_counts['FAIL']}<br/>
        • Warnings: {status_counts['WARNING']}<br/>
        • Pass Rate: {pass_rate:.1f}%
        """
        
        elements.append(Paragraph(stats_text, self.styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_detailed_results(self) -> List:
        """Create detailed test results section"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("Detailed Test Results", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        tests = self.results.get('tests', {})
        
        test_details = {
            'page_load': self._format_page_load,
            'links': self._format_links,
            'forms': self._format_forms,
            'responsive': self._format_responsive,
            'security': self._format_security,
            'accessibility': self._format_accessibility,
            'console_errors': self._format_console_errors
        }
        
        for test_key, test_result in tests.items():
            if test_key in test_details:
                test_elements = test_details[test_key](test_result)
                elements.extend(test_elements)
                elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _format_page_load(self, result: Dict) -> List:
        """Format page load test results"""
        elements = []
        elements.append(Paragraph("📊 Page Load Performance", self.styles['SubsectionHeader']))
        
        status = result.get('status', 'FAIL')
        status_para = Paragraph(f"Status: {status}", self.styles[f'Status{status}'])
        elements.append(status_para)
        
        load_time = result.get('load_time', 'N/A')
        status_code = result.get('status_code', 'N/A')
        page_title = result.get('page_title', 'N/A')
        
        try:
            load_time_display = f"{float(load_time):.2f}s"
        except (TypeError, ValueError):
            load_time_display = f"{load_time}s" if load_time != 'N/A' else 'N/A'
        
        details = f"""
        • <b>Load Time:</b> {load_time_display}<br/>
        • <b>HTTP Status:</b> {status_code}<br/>
        • <b>Page Title:</b> {page_title}
        """
        
        elements.append(Paragraph(details, self.styles['Normal']))
        return elements
    
    def _format_links(self, result: Dict) -> List:
        """Format link test results"""
        elements = []
        elements.append(Paragraph("🔗 Link Validation", self.styles['SubsectionHeader']))
        
        status = result.get('status', 'FAIL')
        status_para = Paragraph(f"Status: {status}", self.styles[f'Status{status}'])
        elements.append(status_para)
        
        total = result.get('total_links', 0)
        internal = result.get('internal_links', 0)
        external = result.get('external_links', 0)
        broken = result.get('broken_links', [])
        
        details = f"""
        • <b>Total Links:</b> {total}<br/>
        • <b>Internal Links:</b> {internal}<br/>
        • <b>External Links:</b> {external}<br/>
        • <b>Broken Links:</b> {len(broken)}
        """
        
        elements.append(Paragraph(details, self.styles['Normal']))
        
        if broken:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("<b>Broken Links:</b>", self.styles['Normal']))
            for link in broken[:5]:  # Show first 5
                elements.append(Paragraph(f"  • {link.get('url', 'N/A')} (Status: {link.get('status', 'N/A')})", 
                                         self.styles['Normal']))
        
        return elements
    
    def _format_forms(self, result: Dict) -> List:
        """Format form test results"""
        elements = []
        elements.append(Paragraph("📝 Form Analysis", self.styles['SubsectionHeader']))
        
        status = result.get('status', 'FAIL')
        status_para = Paragraph(f"Status: {status}", self.styles[f'Status{status}'])
        elements.append(status_para)
        
        total_forms = result.get('total_forms', 0)
        forms = result.get('forms', [])
        
        details = f"• <b>Total Forms:</b> {total_forms}"
        elements.append(Paragraph(details, self.styles['Normal']))
        
        if forms:
            for idx, form in enumerate(forms[:3], 1):  # Show first 3
                form_info = f"""
                  <b>Form {idx}:</b><br/>
                  &nbsp;&nbsp;• Method: {form.get('method', 'N/A')}<br/>
                  &nbsp;&nbsp;• Inputs: {form.get('inputs', 0)}<br/>
                  &nbsp;&nbsp;• Has Submit: {form.get('hasSubmit', False)}
                """
                elements.append(Paragraph(form_info, self.styles['Normal']))
        
        return elements
    
    def _format_responsive(self, result: Dict) -> List:
        """Format responsive design test results"""
        elements = []
        elements.append(Paragraph("📱 Responsive Design", self.styles['SubsectionHeader']))
        
        status = result.get('status', 'FAIL')
        status_para = Paragraph(f"Status: {status}", self.styles[f'Status{status}'])
        elements.append(status_para)
        
        viewports = result.get('viewports', [])
        
        if viewports:
            viewport_data = [['Viewport', 'Size', 'Horizontal Scroll']]
            for vp in viewports:
                viewport_data.append([
                    vp.get('name', 'N/A'),
                    f"{vp.get('width')}x{vp.get('height')}",
                    '⚠ Yes' if vp.get('has_horizontal_scroll') else '✓ No'
                ])
            
            vp_table = Table(viewport_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
            vp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
            ]))
            elements.append(vp_table)
        
        return elements
    
    def _format_security(self, result: Dict) -> List:
        """Format security test results"""
        elements = []
        elements.append(Paragraph("🔒 Security Headers", self.styles['SubsectionHeader']))
        
        status = result.get('status', 'FAIL')
        status_para = Paragraph(f"Status: {status}", self.styles[f'Status{status}'])
        elements.append(status_para)
        
        headers = result.get('headers', {})
        missing = result.get('missing_headers', [])
        
        if headers:
            header_data = [['Header', 'Value']]
            for header, value in headers.items():
                display_value = value if value else '❌ Missing'
                header_data.append([header, str(display_value)[:50]])
            
            header_table = Table(header_data, colWidths=[2.5*inch, 3.5*inch])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
            ]))
            elements.append(header_table)
        
        return elements
    
    def _format_accessibility(self, result: Dict) -> List:
        """Format accessibility test results"""
        elements = []
        elements.append(Paragraph("♿ Accessibility", self.styles['SubsectionHeader']))
        
        status = result.get('status', 'FAIL')
        status_para = Paragraph(f"Status: {status}", self.styles[f'Status{status}'])
        elements.append(status_para)
        
        issues = result.get('issues', [])
        checks = result.get('checks', {})
        
        if checks:
            check_text = f"""
            • <b>Lang Attribute:</b> {'✓' if checks.get('has_lang_attr') else '✗'}<br/>
            • <b>Images with Alt:</b> {checks.get('images_with_alt', 0)}<br/>
            • <b>Images without Alt:</b> {checks.get('images_without_alt', 0)}<br/>
            • <b>Heading Structure:</b> {'✓' if checks.get('has_heading_structure') else '✗'}
            """
            elements.append(Paragraph(check_text, self.styles['Normal']))
        
        if issues:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("<b>Issues Found:</b>", self.styles['Normal']))
            for issue in issues[:5]:
                elements.append(Paragraph(f"  • {issue}", self.styles['Normal']))
        
        return elements
    
    def _format_console_errors(self, result: Dict) -> List:
        """Format console errors test results"""
        elements = []
        elements.append(Paragraph("🐛 Console Errors", self.styles['SubsectionHeader']))
        
        status = result.get('status', 'FAIL')
        status_para = Paragraph(f"Status: {status}", self.styles[f'Status{status}'])
        elements.append(status_para)
        
        errors = result.get('errors', [])
        warnings = result.get('warnings', [])
        
        summary = f"""
        • <b>Errors:</b> {len(errors)}<br/>
        • <b>Warnings:</b> {len(warnings)}
        """
        elements.append(Paragraph(summary, self.styles['Normal']))
        
        if errors:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("<b>Sample Errors:</b>", self.styles['Normal']))
            for error in errors[:3]:
                error_text = str(error)[:100]  # Truncate long errors
                elements.append(Paragraph(f"  • {error_text}", self.styles['Normal']))
        
        return elements
    
    def _add_screenshots(self) -> List:
        """Add screenshots section"""
        elements = []
        
        if not self.screenshots_dir or not self.screenshots_dir.exists():
            return elements
        
        screenshot_files = sorted(self.screenshots_dir.glob("*.png"))
        
        if not screenshot_files:
            return elements
        
        elements.append(PageBreak())
        elements.append(Paragraph("Screenshots", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        for idx, screenshot in enumerate(screenshot_files[:6], 1):  # Max 6 screenshots
            try:
                # Resize image to fit page
                img = PILImage.open(screenshot)
                img_width, img_height = img.size
                
                # Calculate aspect ratio
                max_width = 6 * inch
                max_height = 4 * inch
                
                ratio = min(max_width / img_width, max_height / img_height)
                new_width = img_width * ratio
                new_height = img_height * ratio
                
                elements.append(Paragraph(f"Step {idx}: {screenshot.stem}", self.styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))
                
                img_element = Image(str(screenshot), width=new_width, height=new_height)
                elements.append(img_element)
                elements.append(Spacer(1, 0.2*inch))
                
            except Exception as e:
                elements.append(Paragraph(f"Error loading screenshot: {e}", self.styles['Normal']))
        
        return elements
    
    def _add_recommendations(self) -> List:
        """Add recommendations section"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("Recommendations", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        tests = self.results.get('tests', {})
        recommendations = []
        
        # Analyze results and generate recommendations
        if tests.get('page_load', {}).get('load_time', 0) > 3:
            recommendations.append("⚡ Page load time exceeds 3 seconds. Fix: compress images, minify JS/CSS, and enable browser/server caching.")
        
        if tests.get('links', {}).get('broken_links'):
            recommendations.append("🔗 Broken links detected. Fix: update or remove broken URLs and add automated link checks in CI.")
        
        security = tests.get('security', {})
        if security.get('missing_headers'):
            missing = ', '.join(security.get('missing_headers', [])[:5])
            recommendations.append(f"🔒 Missing security headers: {missing}. Fix: configure these headers at CDN/reverse proxy/app server level.")
        
        accessibility = tests.get('accessibility', {})
        if accessibility.get('issues'):
            recommendations.append("♿ Accessibility issues found. Fix: add alt text, labels, heading hierarchy, and retest against WCAG checks.")
        
        responsive = tests.get('responsive', {})
        if responsive.get('status') == 'WARNING':
            recommendations.append("📱 Responsive design issues detected. Fix: remove horizontal overflow and verify at mobile/tablet/desktop breakpoints.")
        
        console = tests.get('console_errors', {})
        if console.get('errors'):
            recommendations.append("🐛 JavaScript console errors detected. Fix: inspect stack traces, patch failing scripts, and add regression tests.")
        
        if not recommendations:
            recommendations.append("✓ Great job! Your website passed all major tests. Keep monitoring regularly for best results.")
        
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", self.styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def generate(self, output_path: str = None) -> str:
        """Generate the PDF report"""
        if output_path is None:
            # Generate filename
            safe_url = urlparse(self.results.get('url', 'test')).netloc
            safe_url = safe_url.replace('.', '_').replace(':', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"report_{safe_url}_{timestamp}.pdf"
        
        # Convert to Path and handle if already includes directory
        output_path = Path(output_path)
        
        # If output_path is absolute or already includes reports dir, use it directly
        if output_path.is_absolute() or 'reports' in str(output_path.parent):
            full_path = output_path
            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # Ensure reports directory exists
            reports_dir = Path('reports')
            reports_dir.mkdir(exist_ok=True)
            full_path = reports_dir / output_path
        
        # Create PDF
        doc = SimpleDocTemplate(
            str(full_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content
        elements = []
        elements.extend(self._create_header())
        elements.extend(self._create_summary())
        elements.extend(self._create_detailed_results())
        elements.extend(self._add_screenshots())
        elements.extend(self._add_recommendations())
        
        # Build PDF
        doc.build(elements)
        
        return str(full_path)
