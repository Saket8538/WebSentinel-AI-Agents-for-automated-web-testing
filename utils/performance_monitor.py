"""
Performance Monitor
===================

Comprehensive performance monitoring and analysis for web applications.
Tracks page load metrics, Core Web Vitals, resource loading, and system metrics.
"""

import asyncio
import psutil
import time
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import json

from playwright.async_api import Page
from rich.console import Console

console = Console()


class PerformanceMonitor:
    """Monitor and analyze web performance metrics"""
    
    def __init__(self, page: Page):
        self.page = page
        self.metrics = {
            'timestamp': datetime.now().isoformat(),
            'performance_metrics': {},
            'core_web_vitals': {},
            'resource_timing': [],
            'system_metrics': {},
            'network_metrics': {}
        }
    
    async def measure_page_load(self) -> Dict[str, Any]:
        """Measure page load performance"""
        console.print("[cyan]⚡ Measuring page load performance...[/cyan]")
        
        try:
            # Get performance timing
            timing = await self.page.evaluate("""() => {
                const perfData = window.performance.timing;
                const navigation = window.performance.getEntriesByType('navigation')[0];
                
                return {
                    // Legacy timing API
                    dns_lookup: perfData.domainLookupEnd - perfData.domainLookupStart,
                    tcp_connect: perfData.connectEnd - perfData.connectStart,
                    request_time: perfData.responseStart - perfData.requestStart,
                    response_time: perfData.responseEnd - perfData.responseStart,
                    dom_loading: perfData.domLoading - perfData.navigationStart,
                    dom_interactive: perfData.domInteractive - perfData.navigationStart,
                    dom_complete: perfData.domComplete - perfData.navigationStart,
                    load_complete: perfData.loadEventEnd - perfData.navigationStart,
                    
                    // Navigation Timing API Level 2
                    total_page_load: navigation ? navigation.loadEventEnd : 0,
                    redirect_time: navigation ? navigation.redirectEnd - navigation.redirectStart : 0,
                    cache_time: navigation ? navigation.domainLookupStart - navigation.fetchStart : 0,
                    ttfb: navigation ? navigation.responseStart - navigation.requestStart : 0
                };
            }""")
            
            self.metrics['performance_metrics'] = {
                'status': 'PASS',
                'timing': timing,
                'message': f"Page loaded in {timing['load_complete']}ms"
            }
            
            console.print(f"   [green]✓[/green] Total load time: {timing['load_complete']}ms")
            console.print(f"   [green]✓[/green] TTFB: {timing['ttfb']}ms")
            
            return self.metrics['performance_metrics']
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Performance measurement failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to measure performance: {e}"
            }
    
    async def measure_core_web_vitals(self) -> Dict[str, Any]:
        """Measure Core Web Vitals (LCP, FID, CLS)"""
        console.print("[cyan]📊 Measuring Core Web Vitals...[/cyan]")
        
        try:
            # Inject web-vitals library if not present
            await self.page.add_script_tag(
                url='https://unpkg.com/web-vitals@3/dist/web-vitals.iife.js'
            )
            
            # Wait for metrics to be collected
            await asyncio.sleep(2)
            
            vitals = await self.page.evaluate("""() => {
                return new Promise((resolve) => {
                    const vitals = {};
                    
                    // Get LCP (Largest Contentful Paint)
                    if (window.webVitals && window.webVitals.onLCP) {
                        window.webVitals.onLCP((metric) => {
                            vitals.lcp = metric.value;
                        });
                    }
                    
                    // Get FID (First Input Delay)
                    if (window.webVitals && window.webVitals.onFID) {
                        window.webVitals.onFID((metric) => {
                            vitals.fid = metric.value;
                        });
                    }
                    
                    // Get CLS (Cumulative Layout Shift)
                    if (window.webVitals && window.webVitals.onCLS) {
                        window.webVitals.onCLS((metric) => {
                            vitals.cls = metric.value;
                        });
                    }
                    
                    // Get FCP (First Contentful Paint)
                    if (window.webVitals && window.webVitals.onFCP) {
                        window.webVitals.onFCP((metric) => {
                            vitals.fcp = metric.value;
                        });
                    }
                    
                    // Get TTFB (Time to First Byte)
                    if (window.webVitals && window.webVitals.onTTFB) {
                        window.webVitals.onTTFB((metric) => {
                            vitals.ttfb = metric.value;
                        });
                    }
                    
                    setTimeout(() => resolve(vitals), 1000);
                });
            }""")
            
            # Evaluate Core Web Vitals thresholds
            lcp_status = 'GOOD' if vitals.get('lcp', 0) < 2500 else 'POOR' if vitals.get('lcp', 0) > 4000 else 'NEEDS_IMPROVEMENT'
            fid_status = 'GOOD' if vitals.get('fid', 0) < 100 else 'POOR' if vitals.get('fid', 0) > 300 else 'NEEDS_IMPROVEMENT'
            cls_status = 'GOOD' if vitals.get('cls', 0) < 0.1 else 'POOR' if vitals.get('cls', 0) > 0.25 else 'NEEDS_IMPROVEMENT'
            
            self.metrics['core_web_vitals'] = {
                'status': 'PASS' if all(s == 'GOOD' for s in [lcp_status, fid_status, cls_status]) else 'WARNING',
                'vitals': vitals,
                'ratings': {
                    'lcp': lcp_status,
                    'fid': fid_status,
                    'cls': cls_status
                },
                'message': f"LCP: {vitals.get('lcp', 'N/A')}ms, FID: {vitals.get('fid', 'N/A')}ms, CLS: {vitals.get('cls', 'N/A')}"
            }
            
            console.print(f"   [green]✓[/green] LCP: {vitals.get('lcp', 'N/A')}ms ({lcp_status})")
            console.print(f"   [green]✓[/green] FID: {vitals.get('fid', 'N/A')}ms ({fid_status})")
            console.print(f"   [green]✓[/green] CLS: {vitals.get('cls', 'N/A')} ({cls_status})")
            
            return self.metrics['core_web_vitals']
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Core Web Vitals measurement failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to measure Core Web Vitals: {e}"
            }
    
    async def analyze_resource_loading(self) -> Dict[str, Any]:
        """Analyze resource loading performance"""
        console.print("[cyan]📦 Analyzing resource loading...[/cyan]")
        
        try:
            resources = await self.page.evaluate("""() => {
                const entries = performance.getEntriesByType('resource');
                const resourceTypes = {};
                
                entries.forEach(entry => {
                    const type = entry.initiatorType || 'other';
                    if (!resourceTypes[type]) {
                        resourceTypes[type] = {
                            count: 0,
                            total_size: 0,
                            total_duration: 0,
                            resources: []
                        };
                    }
                    
                    resourceTypes[type].count++;
                    resourceTypes[type].total_size += entry.transferSize || 0;
                    resourceTypes[type].total_duration += entry.duration || 0;
                    resourceTypes[type].resources.push({
                        name: entry.name,
                        duration: entry.duration,
                        size: entry.transferSize
                    });
                });
                
                return {
                    total_resources: entries.length,
                    by_type: resourceTypes,
                    total_size: entries.reduce((sum, e) => sum + (e.transferSize || 0), 0),
                    total_duration: entries.reduce((sum, e) => sum + (e.duration || 0), 0)
                };
            }""")
            
            self.metrics['resource_timing'] = {
                'status': 'PASS',
                'resources': resources,
                'message': f"Analyzed {resources['total_resources']} resources"
            }
            
            console.print(f"   [green]✓[/green] Total resources: {resources['total_resources']}")
            console.print(f"   [green]✓[/green] Total size: {resources['total_size'] / 1024:.2f} KB")
            
            return self.metrics['resource_timing']
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Resource analysis failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to analyze resources: {e}"
            }
    
    def measure_system_metrics(self) -> Dict[str, Any]:
        """Measure system resource usage"""
        console.print("[cyan]💻 Measuring system metrics...[/cyan]")
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.metrics['system_metrics'] = {
                'status': 'PASS',
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available / (1024 * 1024),
                'disk_percent': disk.percent,
                'message': f"CPU: {cpu_percent}%, Memory: {memory.percent}%"
            }
            
            console.print(f"   [green]✓[/green] CPU usage: {cpu_percent}%")
            console.print(f"   [green]✓[/green] Memory usage: {memory.percent}%")
            
            return self.metrics['system_metrics']
            
        except Exception as e:
            console.print(f"   [red]✗[/red] System metrics measurement failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to measure system metrics: {e}"
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all performance tests"""
        console.print("\n[bold cyan]⚡ Running Performance Tests[/bold cyan]\n")
        
        await self.measure_page_load()
        await self.measure_core_web_vitals()
        await self.analyze_resource_loading()
        self.measure_system_metrics()
        
        # Calculate overall status
        statuses = [
            self.metrics.get('performance_metrics', {}).get('status'),
            self.metrics.get('core_web_vitals', {}).get('status'),
            self.metrics.get('resource_timing', {}).get('status'),
            self.metrics.get('system_metrics', {}).get('status')
        ]
        
        if 'FAIL' in statuses:
            self.metrics['overall_status'] = 'FAIL'
        elif 'WARNING' in statuses:
            self.metrics['overall_status'] = 'WARNING'
        else:
            self.metrics['overall_status'] = 'PASS'
        
        return self.metrics
    
    def save_results(self, output_dir: str = 'performance_results'):
        """Save performance results to JSON"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"performance_{timestamp}.json"
        
        filepath = output_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2)
        
        console.print(f"\n[green]✓[/green] Performance results saved to: {filepath}")
        return str(filepath)
