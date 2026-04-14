"""
SEO Analyzer
=============

Comprehensive SEO analysis tool for web applications.
Checks meta tags, Open Graph, structured data, robots.txt, sitemap, and more.
"""

import asyncio
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from urllib.parse import urljoin, urlparse
import json

from playwright.async_api import Page
from rich.console import Console

console = Console()


class SEOAnalyzer:
    """Analyze SEO aspects of web applications"""
    
    def __init__(self, url: str, page: Page):
        self.url = url
        self.page = page
        self.results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'seo_checks': {}
        }
    
    async def check_meta_tags(self) -> Dict[str, Any]:
        """Check essential meta tags"""
        console.print("[cyan]🏷️  Checking meta tags...[/cyan]")
        
        try:
            meta_data = await self.page.evaluate("""() => {
                const getMeta = (name) => {
                    const meta = document.querySelector(`meta[name="${name}"]`) || 
                                document.querySelector(`meta[property="${name}"]`);
                    return meta ? meta.getAttribute('content') : null;
                };
                
                return {
                    title: document.title,
                    description: getMeta('description'),
                    keywords: getMeta('keywords'),
                    author: getMeta('author'),
                    viewport: getMeta('viewport'),
                    robots: getMeta('robots'),
                    canonical: document.querySelector('link[rel="canonical"]')?.href,
                    
                    // Character count
                    title_length: document.title.length,
                    description_length: getMeta('description')?.length || 0
                };
            }""")
            
            issues = []
            
            # Check title
            if not meta_data['title']:
                issues.append("Missing page title")
            elif meta_data['title_length'] < 30 or meta_data['title_length'] > 60:
                issues.append(f"Title length ({meta_data['title_length']}) should be 30-60 characters")
            
            # Check description
            if not meta_data['description']:
                issues.append("Missing meta description")
            elif meta_data['description_length'] < 120 or meta_data['description_length'] > 160:
                issues.append(f"Description length ({meta_data['description_length']}) should be 120-160 characters")
            
            # Check viewport
            if not meta_data['viewport']:
                issues.append("Missing viewport meta tag")
            
            # Check canonical
            if not meta_data['canonical']:
                issues.append("Missing canonical URL")
            
            self.results['seo_checks']['meta_tags'] = {
                'status': 'WARNING' if issues else 'PASS',
                'meta_data': meta_data,
                'issues': issues,
                'message': f"Found {len(issues)} meta tag issue(s)" if issues else "All essential meta tags present"
            }
            
            console.print(f"   [green]✓[/green] Title: {meta_data['title'][:50]}...")
            if issues:
                console.print(f"   [yellow]⚠[/yellow] Issues: {len(issues)}")
                for issue in issues[:3]:
                    console.print(f"      • {issue}")
            
            return self.results['seo_checks']['meta_tags']
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Meta tag check failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to check meta tags: {e}"
            }
    
    async def check_open_graph(self) -> Dict[str, Any]:
        """Check Open Graph tags for social media"""
        console.print("[cyan]📱 Checking Open Graph tags...[/cyan]")
        
        try:
            og_data = await self.page.evaluate("""() => {
                const getOG = (property) => {
                    const meta = document.querySelector(`meta[property="og:${property}"]`);
                    return meta ? meta.getAttribute('content') : null;
                };
                
                return {
                    title: getOG('title'),
                    description: getOG('description'),
                    image: getOG('image'),
                    url: getOG('url'),
                    type: getOG('type'),
                    site_name: getOG('site_name'),
                    
                    // Twitter Cards
                    twitter_card: document.querySelector('meta[name="twitter:card"]')?.content,
                    twitter_site: document.querySelector('meta[name="twitter:site"]')?.content,
                    twitter_title: document.querySelector('meta[name="twitter:title"]')?.content,
                    twitter_description: document.querySelector('meta[name="twitter:description"]')?.content,
                    twitter_image: document.querySelector('meta[name="twitter:image"]')?.content
                };
            }""")
            
            issues = []
            if not og_data['title']:
                issues.append("Missing og:title")
            if not og_data['description']:
                issues.append("Missing og:description")
            if not og_data['image']:
                issues.append("Missing og:image")
            if not og_data['twitter_card']:
                issues.append("Missing Twitter Card tags")
            
            self.results['seo_checks']['open_graph'] = {
                'status': 'WARNING' if issues else 'PASS',
                'og_data': og_data,
                'issues': issues,
                'message': f"Found {len(issues)} Open Graph issue(s)" if issues else "All Open Graph tags present"
            }
            
            console.print(f"   [green]✓[/green] OG Title: {og_data.get('title', 'N/A')[:50]}")
            if issues:
                console.print(f"   [yellow]⚠[/yellow] Issues: {len(issues)}")
            
            return self.results['seo_checks']['open_graph']
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Open Graph check failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to check Open Graph: {e}"
            }
    
    async def check_structured_data(self) -> Dict[str, Any]:
        """Check for structured data (JSON-LD, microdata)"""
        console.print("[cyan]🔍 Checking structured data...[/cyan]")
        
        try:
            structured_data = await self.page.evaluate("""() => {
                const jsonLD = [];
                document.querySelectorAll('script[type="application/ld+json"]').forEach(script => {
                    try {
                        jsonLD.push(JSON.parse(script.textContent));
                    } catch(e) {
                        console.error('Failed to parse JSON-LD', e);
                    }
                });
                
                const microdata = document.querySelectorAll('[itemscope]').length;
                
                return {
                    json_ld_count: jsonLD.length,
                    json_ld_schemas: jsonLD,
                    microdata_count: microdata
                };
            }""")
            
            has_structured_data = structured_data['json_ld_count'] > 0 or structured_data['microdata_count'] > 0
            
            self.results['seo_checks']['structured_data'] = {
                'status': 'PASS' if has_structured_data else 'WARNING',
                'structured_data': structured_data,
                'message': f"Found {structured_data['json_ld_count']} JSON-LD schema(s) and {structured_data['microdata_count']} microdata item(s)"
            }
            
            console.print(f"   [green]✓[/green] JSON-LD schemas: {structured_data['json_ld_count']}")
            console.print(f"   [green]✓[/green] Microdata items: {structured_data['microdata_count']}")
            
            return self.results['seo_checks']['structured_data']
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Structured data check failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to check structured data: {e}"
            }
    
    async def check_headings(self) -> Dict[str, Any]:
        """Check heading structure (H1-H6)"""
        console.print("[cyan]📋 Checking heading structure...[/cyan]")
        
        try:
            headings = await self.page.evaluate("""() => {
                const getHeadings = (tag) => {
                    return Array.from(document.querySelectorAll(tag)).map(h => ({
                        text: h.textContent.trim().substring(0, 100),
                        level: tag
                    }));
                };
                
                return {
                    h1: getHeadings('h1'),
                    h2: getHeadings('h2'),
                    h3: getHeadings('h3'),
                    h4: getHeadings('h4'),
                    h5: getHeadings('h5'),
                    h6: getHeadings('h6'),
                    h1_count: document.querySelectorAll('h1').length
                };
            }""")
            
            issues = []
            if headings['h1_count'] == 0:
                issues.append("No H1 heading found")
            elif headings['h1_count'] > 1:
                issues.append(f"Multiple H1 headings found ({headings['h1_count']})")
            
            self.results['seo_checks']['headings'] = {
                'status': 'WARNING' if issues else 'PASS',
                'headings': headings,
                'issues': issues,
                'message': f"H1: {headings['h1_count']}, H2: {len(headings['h2'])}, H3: {len(headings['h3'])}"
            }
            
            console.print(f"   [green]✓[/green] H1 count: {headings['h1_count']}")
            console.print(f"   [green]✓[/green] H2 count: {len(headings['h2'])}")
            if issues:
                console.print(f"   [yellow]⚠[/yellow] Issues: {', '.join(issues)}")
            
            return self.results['seo_checks']['headings']
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Heading check failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to check headings: {e}"
            }
    
    def check_robots_txt(self) -> Dict[str, Any]:
        """Check robots.txt file"""
        console.print("[cyan]🤖 Checking robots.txt...[/cyan]")
        
        try:
            parsed_url = urlparse(self.url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            response = requests.get(robots_url, timeout=10)
            
            if response.status_code == 200:
                robots_content = response.text
                has_sitemap = 'Sitemap:' in robots_content
                has_user_agent = 'User-agent:' in robots_content
                
                self.results['seo_checks']['robots_txt'] = {
                    'status': 'PASS',
                    'exists': True,
                    'content': robots_content,
                    'has_sitemap': has_sitemap,
                    'has_user_agent': has_user_agent,
                    'message': "robots.txt found and accessible"
                }
                
                console.print(f"   [green]✓[/green] robots.txt exists")
                if has_sitemap:
                    console.print(f"   [green]✓[/green] Sitemap reference found")
            else:
                self.results['seo_checks']['robots_txt'] = {
                    'status': 'WARNING',
                    'exists': False,
                    'status_code': response.status_code,
                    'message': f"robots.txt not found (status: {response.status_code})"
                }
                console.print(f"   [yellow]⚠[/yellow] robots.txt not found")
            
            return self.results['seo_checks']['robots_txt']
            
        except Exception as e:
            console.print(f"   [red]✗[/red] robots.txt check failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to check robots.txt: {e}"
            }
    
    def check_sitemap(self) -> Dict[str, Any]:
        """Check sitemap.xml file"""
        console.print("[cyan]🗺️  Checking sitemap.xml...[/cyan]")
        
        try:
            parsed_url = urlparse(self.url)
            sitemap_urls = [
                f"{parsed_url.scheme}://{parsed_url.netloc}/sitemap.xml",
                f"{parsed_url.scheme}://{parsed_url.netloc}/sitemap_index.xml"
            ]
            
            for sitemap_url in sitemap_urls:
                response = requests.get(sitemap_url, timeout=10)
                
                if response.status_code == 200:
                    # Parse sitemap XML
                    soup = BeautifulSoup(response.content, 'xml')
                    urls = soup.find_all('url')
                    sitemaps = soup.find_all('sitemap')
                    
                    self.results['seo_checks']['sitemap'] = {
                        'status': 'PASS',
                        'exists': True,
                        'url': sitemap_url,
                        'url_count': len(urls),
                        'sitemap_count': len(sitemaps),
                        'message': f"Sitemap found with {len(urls)} URL(s)"
                    }
                    
                    console.print(f"   [green]✓[/green] Sitemap exists at {sitemap_url}")
                    console.print(f"   [green]✓[/green] Contains {len(urls)} URL(s)")
                    return self.results['seo_checks']['sitemap']
            
            # If no sitemap found
            self.results['seo_checks']['sitemap'] = {
                'status': 'WARNING',
                'exists': False,
                'message': "Sitemap not found"
            }
            console.print(f"   [yellow]⚠[/yellow] Sitemap not found")
            return self.results['seo_checks']['sitemap']
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Sitemap check failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to check sitemap: {e}"
            }
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all SEO checks"""
        console.print("\n[bold cyan]🔍 Running SEO Analysis[/bold cyan]\n")
        
        await self.check_meta_tags()
        await self.check_open_graph()
        await self.check_structured_data()
        await self.check_headings()
        self.check_robots_txt()
        self.check_sitemap()
        
        # Calculate overall status
        statuses = [check.get('status') for check in self.results['seo_checks'].values()]
        
        if 'FAIL' in statuses:
            self.results['overall_status'] = 'FAIL'
        elif 'WARNING' in statuses:
            self.results['overall_status'] = 'WARNING'
        else:
            self.results['overall_status'] = 'PASS'
        
        return self.results
    
    def save_results(self, output_dir: str = 'seo_results'):
        """Save SEO results to JSON"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        safe_url = urlparse(self.url).netloc.replace('.', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"seo_{safe_url}_{timestamp}.json"
        
        filepath = output_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        console.print(f"\n[green]✓[/green] SEO results saved to: {filepath}")
        return str(filepath)
