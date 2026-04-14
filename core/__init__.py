"""
WebSentinel Core Module
Exports all core components for easy importing
"""

# AI and Analysis
from .ai_analyzer import AIAnalyzer

# Comprehensive Testing
from .comprehensive_tester import ComprehensiveTester

# PDF Generators
from .enhanced_pdf_generator import EnhancedPDFReportGenerator
from .ultra_pdf_generator import UltraEnhancedPDFGenerator

# SEO Analysis
from .seo_analyzer import SEOAnalyzer

# Next-Level AI Features
from .visual_regression import VisualRegressionTester
from .security_scanner import SecurityScanner
from .accessibility_analyzer import AccessibilityAnalyzer, ContrastChecker
from .performance_predictor import PerformancePredictor

# New Modules
from .site_crawler import SiteCrawler
from .lighthouse_runner import LighthouseRunner

__all__ = [
    # AI
    'AIAnalyzer',
    
    # Testing
    'ComprehensiveTester',
    
    # PDF
    'EnhancedPDFReportGenerator',
    'UltraEnhancedPDFGenerator',
    
    # SEO
    'SEOAnalyzer',
    
    # Next-Level Features
    'VisualRegressionTester',
    'SecurityScanner',
    'AccessibilityAnalyzer',
    'ContrastChecker',
    'PerformancePredictor',
    
    # New Modules
    'SiteCrawler',
    'LighthouseRunner',
]
