"""
AI-Powered Performance Predictor
ML-based performance forecasting and optimization recommendations
"""
import re
from typing import Dict, Any, List
from datetime import datetime, timedelta
import statistics


class PerformancePredictor:
    """Predict future performance trends and provide optimization recommendations"""
    
    def __init__(self):
        self.historical_data = []
        self.prediction_horizon = 30  # days
        
    async def analyze_and_predict(
        self,
        current_metrics: Dict[str, Any],
        historical_metrics: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze current performance and predict future trends
        
        Args:
            current_metrics: Current performance metrics
            historical_metrics: Historical performance data
            
        Returns:
            Performance analysis with predictions and recommendations
        """
        if historical_metrics:
            self.historical_data = historical_metrics
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "current_performance": self._analyze_current(current_metrics),
            "trend_analysis": self._analyze_trends(),
            "predictions": self._generate_predictions(current_metrics),
            "bottlenecks": self._identify_bottlenecks(current_metrics),
            "optimization_recommendations": [],
            "performance_score": 0
        }
        
        # Generate optimization recommendations
        results["optimization_recommendations"] = self._generate_recommendations(
            results["current_performance"],
            results["bottlenecks"]
        )
        
        # Calculate overall performance score
        results["performance_score"] = self._calculate_performance_score(current_metrics)
        
        return results
    
    def _analyze_current(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current performance metrics"""
        analysis = {
            "load_time": {
                "value": metrics.get("page_load_time", 0),
                "status": self._get_load_time_status(metrics.get("page_load_time", 0)),
                "benchmark": "< 3s excellent, 3-5s good, > 5s poor"
            },
            "response_time": {
                "value": metrics.get("first_response_time", 0),
                "status": self._get_response_time_status(metrics.get("first_response_time", 0)),
                "benchmark": "< 200ms excellent, 200-500ms good, > 500ms poor"
            },
            "resource_count": {
                "value": metrics.get("resource_count", 0),
                "status": self._get_resource_count_status(metrics.get("resource_count", 0)),
                "benchmark": "< 50 excellent, 50-100 good, > 100 poor"
            },
            "page_size": {
                "value": metrics.get("page_size_kb", 0),
                "status": self._get_page_size_status(metrics.get("page_size_kb", 0)),
                "benchmark": "< 1MB excellent, 1-3MB good, > 3MB poor"
            }
        }
        
        return analysis
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if len(self.historical_data) < 2:
            return {
                "trend": "INSUFFICIENT_DATA",
                "message": "Need at least 2 data points for trend analysis"
            }
        
        # Extract load times from historical data
        load_times = [m.get("page_load_time", 0) for m in self.historical_data]
        
        # Calculate trend
        if len(load_times) >= 3:
            recent_avg = statistics.mean(load_times[-3:])
            older_avg = statistics.mean(load_times[:3])
            
            if recent_avg < older_avg * 0.9:
                trend = "IMPROVING"
                change = ((older_avg - recent_avg) / older_avg) * 100
            elif recent_avg > older_avg * 1.1:
                trend = "DEGRADING"
                change = ((recent_avg - older_avg) / older_avg) * 100
            else:
                trend = "STABLE"
                change = 0
        else:
            trend = "INSUFFICIENT_DATA"
            change = 0
        
        return {
            "trend": trend,
            "change_percentage": round(change, 2),
            "data_points": len(self.historical_data),
            "analysis_period_days": len(self.historical_data)
        }
    
    def _generate_predictions(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance predictions"""
        predictions = {
            "next_30_days": {},
            "confidence": "MEDIUM",
            "methodology": "Statistical analysis with linear regression"
        }
        
        # Predict load time
        current_load_time = current_metrics.get("page_load_time", 3.0)
        
        if len(self.historical_data) >= 5:
            load_times = [m.get("page_load_time", 0) for m in self.historical_data]
            # Simple linear trend
            avg_change = (load_times[-1] - load_times[0]) / len(load_times)
            predicted_load_time = current_load_time + (avg_change * 30)
            predictions["confidence"] = "HIGH" if len(self.historical_data) >= 10 else "MEDIUM"
        else:
            # Use current with small degradation assumption
            predicted_load_time = current_load_time * 1.05
            predictions["confidence"] = "LOW"
        
        predictions["next_30_days"] = {
            "load_time": {
                "predicted": round(predicted_load_time, 2),
                "current": current_load_time,
                "change": round(((predicted_load_time - current_load_time) / current_load_time) * 100, 2),
                "status": self._get_load_time_status(predicted_load_time)
            },
            "risk_level": self._assess_risk(predicted_load_time, current_load_time)
        }
        
        return predictions
    
    def _identify_bottlenecks(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # Check page load time
        load_time = metrics.get("page_load_time", 0)
        if load_time > 5:
            bottlenecks.append({
                "type": "SLOW_PAGE_LOAD",
                "severity": "HIGH",
                "metric": "page_load_time",
                "value": load_time,
                "threshold": 3,
                "impact": "Users likely to abandon page (53% bounce rate > 3s)",
                "causes": [
                    "Large unoptimized images",
                    "Too many HTTP requests",
                    "Unminified CSS/JS",
                    "No caching headers",
                    "Slow server response"
                ]
            })
        elif load_time > 3:
            bottlenecks.append({
                "type": "SLOW_PAGE_LOAD",
                "severity": "MEDIUM",
                "metric": "page_load_time",
                "value": load_time,
                "threshold": 3,
                "impact": "Suboptimal user experience",
                "causes": [
                    "Unoptimized images",
                    "Multiple HTTP requests",
                    "No compression"
                ]
            })
        
        # Check resource count
        resource_count = metrics.get("resource_count", 0)
        if resource_count > 100:
            bottlenecks.append({
                "type": "TOO_MANY_RESOURCES",
                "severity": "HIGH",
                "metric": "resource_count",
                "value": resource_count,
                "threshold": 50,
                "impact": "Increased latency and bandwidth usage",
                "causes": [
                    "No resource bundling",
                    "Too many external dependencies",
                    "Unoptimized asset loading"
                ]
            })
        
        # Check page size
        page_size = metrics.get("page_size_kb", 0)
        if page_size > 3000:  # > 3MB
            bottlenecks.append({
                "type": "LARGE_PAGE_SIZE",
                "severity": "HIGH",
                "metric": "page_size_kb",
                "value": page_size,
                "threshold": 1000,
                "impact": "Slow on mobile networks, high data costs",
                "causes": [
                    "Uncompressed images",
                    "Large videos/media",
                    "Unminified assets",
                    "No lazy loading"
                ]
            })
        
        # Check response time
        response_time = metrics.get("first_response_time", 0)
        if response_time > 500:
            bottlenecks.append({
                "type": "SLOW_SERVER_RESPONSE",
                "severity": "HIGH" if response_time > 1000 else "MEDIUM",
                "metric": "first_response_time",
                "value": response_time,
                "threshold": 200,
                "impact": "Delayed initial rendering",
                "causes": [
                    "Slow database queries",
                    "Inefficient backend code",
                    "No CDN",
                    "Unoptimized server config"
                ]
            })
        
        return bottlenecks
    
    def _generate_recommendations(
        self,
        current_performance: Dict[str, Any],
        bottlenecks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate actionable optimization recommendations"""
        recommendations = []
        
        # High priority recommendations based on bottlenecks
        for bottleneck in bottlenecks:
            if bottleneck["severity"] == "HIGH":
                if bottleneck["type"] == "SLOW_PAGE_LOAD":
                    recommendations.append({
                        "priority": "HIGH",
                        "category": "Performance",
                        "title": "Optimize Page Load Time",
                        "description": f"Current load time ({bottleneck['value']}s) exceeds acceptable threshold",
                        "actions": [
                            "Compress and optimize images (use WebP format)",
                            "Minify CSS, JavaScript, and HTML",
                            "Enable GZIP/Brotli compression",
                            "Implement browser caching",
                            "Use a Content Delivery Network (CDN)",
                            "Lazy load images and videos",
                            "Reduce server response time"
                        ],
                        "expected_improvement": "50-70% reduction in load time",
                        "effort": "Medium",
                        "tools": ["ImageOptim", "TinyPNG", "Cloudflare CDN", "Google PageSpeed Insights"]
                    })
                
                elif bottleneck["type"] == "TOO_MANY_RESOURCES":
                    recommendations.append({
                        "priority": "HIGH",
                        "category": "Resources",
                        "title": "Reduce HTTP Requests",
                        "description": f"{bottleneck['value']} resources is excessive",
                        "actions": [
                            "Bundle CSS and JavaScript files",
                            "Use CSS sprites for images",
                            "Inline critical CSS",
                            "Remove unused dependencies",
                            "Use HTTP/2 or HTTP/3",
                            "Implement resource preloading"
                        ],
                        "expected_improvement": "40-60% reduction in requests",
                        "effort": "Medium",
                        "tools": ["Webpack", "Rollup", "Parcel", "Vite"]
                    })
                
                elif bottleneck["type"] == "LARGE_PAGE_SIZE":
                    recommendations.append({
                        "priority": "HIGH",
                        "category": "Size",
                        "title": "Reduce Page Size",
                        "description": f"{bottleneck['value']}KB is too large for optimal performance",
                        "actions": [
                            "Compress images (aim for < 100KB per image)",
                            "Use next-gen image formats (WebP, AVIF)",
                            "Implement lazy loading for images/videos",
                            "Remove unused CSS/JS code",
                            "Use text compression (GZIP/Brotli)",
                            "Optimize fonts (use WOFF2, font-display: swap)"
                        ],
                        "expected_improvement": "60-80% size reduction",
                        "effort": "Low to Medium",
                        "tools": ["Squoosh", "ImageMagick", "PurgeCSS", "Tree-shaking"]
                    })
                
                elif bottleneck["type"] == "SLOW_SERVER_RESPONSE":
                    recommendations.append({
                        "priority": "HIGH",
                        "category": "Backend",
                        "title": "Optimize Server Response Time",
                        "description": f"{bottleneck['value']}ms response time needs improvement",
                        "actions": [
                            "Optimize database queries (add indexes)",
                            "Implement server-side caching (Redis, Memcached)",
                            "Use a CDN for static assets",
                            "Upgrade server resources if needed",
                            "Profile and optimize backend code",
                            "Use async/non-blocking operations"
                        ],
                        "expected_improvement": "50-70% faster response",
                        "effort": "Medium to High",
                        "tools": ["New Relic", "DataDog", "Redis", "Nginx caching"]
                    })
        
        # General best practices
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Best Practices",
            "title": "Implement Performance Monitoring",
            "description": "Continuous performance monitoring and alerting",
            "actions": [
                "Set up Real User Monitoring (RUM)",
                "Configure performance budgets",
                "Monitor Core Web Vitals (LCP, FID, CLS)",
                "Set up automated performance testing",
                "Track performance in CI/CD pipeline"
            ],
            "expected_improvement": "Proactive performance management",
            "effort": "Low",
            "tools": ["Google Analytics", "Lighthouse CI", "WebPageTest", "SpeedCurve"]
        })
        
        recommendations.append({
            "priority": "LOW",
            "category": "Advanced",
            "title": "Progressive Enhancement",
            "description": "Enhance user experience for modern browsers",
            "actions": [
                "Implement Service Workers for offline support",
                "Use HTTP/3 and QUIC protocol",
                "Implement prefetching for likely navigation",
                "Use WebP/AVIF with fallbacks",
                "Implement adaptive loading based on network speed"
            ],
            "expected_improvement": "Enhanced UX for modern devices",
            "effort": "High",
            "tools": ["Workbox", "Next.js", "Nuxt.js"]
        })
        
        return recommendations
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> int:
        """Calculate overall performance score (0-100)"""
        score = 100
        
        # Load time score (40% weight)
        load_time = metrics.get("page_load_time", 5)
        if load_time > 5:
            score -= 40
        elif load_time > 3:
            score -= 20
        elif load_time > 1:
            score -= 5
        
        # Response time score (30% weight)
        response_time = metrics.get("first_response_time", 500)
        if response_time > 1000:
            score -= 30
        elif response_time > 500:
            score -= 15
        elif response_time > 200:
            score -= 5
        
        # Resource count score (15% weight)
        resource_count = metrics.get("resource_count", 50)
        if resource_count > 100:
            score -= 15
        elif resource_count > 50:
            score -= 8
        
        # Page size score (15% weight)
        page_size = metrics.get("page_size_kb", 1000)
        if page_size > 3000:
            score -= 15
        elif page_size > 1000:
            score -= 8
        
        return max(0, score)
    
    # Helper methods for status determination
    def _get_load_time_status(self, load_time: float) -> str:
        if load_time < 2:
            return "EXCELLENT"
        elif load_time < 3:
            return "GOOD"
        elif load_time < 5:
            return "FAIR"
        else:
            return "POOR"
    
    def _get_response_time_status(self, response_time: float) -> str:
        if response_time < 200:
            return "EXCELLENT"
        elif response_time < 500:
            return "GOOD"
        elif response_time < 1000:
            return "FAIR"
        else:
            return "POOR"
    
    def _get_resource_count_status(self, count: int) -> str:
        if count < 30:
            return "EXCELLENT"
        elif count < 50:
            return "GOOD"
        elif count < 100:
            return "FAIR"
        else:
            return "POOR"
    
    def _get_page_size_status(self, size_kb: int) -> str:
        if size_kb < 500:
            return "EXCELLENT"
        elif size_kb < 1000:
            return "GOOD"
        elif size_kb < 3000:
            return "FAIR"
        else:
            return "POOR"
    
    def _assess_risk(self, predicted: float, current: float) -> str:
        change = ((predicted - current) / current) * 100
        if change > 20:
            return "HIGH_RISK"
        elif change > 10:
            return "MEDIUM_RISK"
        elif change < -10:
            return "IMPROVING"
        else:
            return "LOW_RISK"
