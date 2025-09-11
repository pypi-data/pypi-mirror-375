"""
ScannerTester - Clean stealth testing through UnrealOn scanner

Provides streamlined stealth testing using our detection service with Pydantic models.
"""

import logging
import asyncio
from typing import Optional, List
from playwright.async_api import Page

from unrealon_core.config.urls import get_url_config
from unrealon_browser.dto import BotDetectionResults, BotDetectionResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ScannerTester:
    """Clean stealth testing through UnrealOn scanner"""

    def __init__(self, logger_bridge=None):
        """Initialize ScannerTester"""
        self.logger_bridge = logger_bridge

    def _log(self, message: str, level: str = "info") -> None:
        """Log message with bridge support"""
        if self.logger_bridge:
            getattr(self.logger_bridge, f"log_{level}", self.logger_bridge.log_info)(message)
        else:
            getattr(logger, level, logger.info)(message)

    def _get_scanner_url(self) -> str:
        """Get scanner URL from configuration"""
        return get_url_config().stealth_test_url

    async def test_stealth(self, browser_manager, stealth_manager, method: str = "comprehensive") -> BotDetectionResponse:
        """
        Test stealth effectiveness with specified method
        
        Args:
            browser_manager: Browser manager instance
            stealth_manager: Stealth manager instance  
            method: Stealth method to use
            
        Returns:
            BotDetectionResponse with results
        """
        if not browser_manager or not browser_manager.page:
            return BotDetectionResponse.error_response(
                "Browser manager or page not available",
                "browser_error",
                self._get_scanner_url()
            )

        try:
            scanner_url = self._get_scanner_url()
            self._log(f"🔬 Testing stealth with method: {method}")
            
            # Apply stealth
            stealth_applied = await stealth_manager.apply_stealth(browser_manager.page, method=method)
            if not stealth_applied:
                return BotDetectionResponse.error_response(
                    f"Failed to apply stealth method: {method}",
                    "stealth_error",
                    scanner_url,
                    method
                )

            # Navigate to scanner
            nav_result = await browser_manager.navigate_async(scanner_url)
            if not nav_result["success"]:
                return BotDetectionResponse.error_response(
                    f"Navigation failed: {nav_result.get('error', 'Unknown error')}",
                    "navigation_error",
                    scanner_url,
                    method
                )

            # Setup console logging to catch JavaScript errors
            await self._setup_console_logging(browser_manager.page)
            
            # Wait for scanner to complete
            await self._wait_for_scanner(browser_manager)
            
            # Extract and parse results
            bot_results = await self._extract_bot_results(browser_manager.page)
            if bot_results:
                return BotDetectionResponse.success_response(bot_results, scanner_url, method)
            else:
                return BotDetectionResponse.error_response(
                    "Scanner results not available or invalid",
                    "extraction_error", 
                    scanner_url,
                    method
                )

        except Exception as e:
            self._log(f"❌ Stealth test failed: {e}", "error")
            return BotDetectionResponse.error_response(
                str(e),
                "test_error",
                self._get_scanner_url(),
                method
            )

    async def compare_methods(self, browser_manager, stealth_manager, methods: Optional[List[str]] = None) -> List[BotDetectionResponse]:
        """
        Compare multiple stealth methods
        
        Args:
            browser_manager: Browser manager instance
            stealth_manager: Stealth manager instance
            methods: List of methods to test (default: ["playwright", "comprehensive", "aggressive"])
            
        Returns:
            List of BotDetectionResponse for each method
        """
        if methods is None:
            methods = ["playwright", "comprehensive", "aggressive"]
            
        self._log(f"🔬 Comparing {len(methods)} stealth methods")
        
        results = []
        for method in methods:
            self._log(f"🧪 Testing method: {method}")
            result = await self.test_stealth(browser_manager, stealth_manager, method)
            results.append(result)
            
            # Brief pause between tests
            await asyncio.sleep(1)
            
        return results

    async def _setup_console_logging(self, page) -> None:
        """Setup console error logging to debug React issues"""
        def handle_console_message(msg):
            if msg.type in ['error', 'warning']:
                self._log(f"🔍 CONSOLE {msg.type.upper()}: {msg.text}", "warning")
            elif msg.type == 'log' and ('error' in msg.text.lower() or 'failed' in msg.text.lower()):
                self._log(f"🔍 CONSOLE LOG: {msg.text}", "info")
        
        page.on("console", handle_console_message)
        self._log("🔍 Console logging enabled for JavaScript error detection", "info")

    async def _wait_for_scanner(self, browser_manager) -> None:
        """Wait for scanner to complete tests using proper page wait methods"""
        self._log("⏳ Waiting for React SPA and bot detection tests...")
        
        # Use proper SPA wait method
        if hasattr(browser_manager, 'page_wait') and browser_manager.page_wait:
            self._log("🚀 Using SPA wait method...")
            spa_ready = await browser_manager.page_wait.wait_spa()
            if not spa_ready:
                self._log("⚠️ SPA wait timeout, trying full load method", "warning")
                await browser_manager.page_wait.wait_full_load()
        else:
            # Fallback to basic wait
            try:
                await browser_manager.page.wait_for_load_state("networkidle", timeout=15000)
            except Exception as e:
                self._log(f"⚠️ Basic load timeout: {e}", "warning")
        
        # Now wait for bot detection results to appear
        self._log("⏳ Waiting for bot detection results...")
        
        max_attempts = 45  # 45 seconds for bot detection
        attempt = 0
        
        while attempt < max_attempts:
            try:
                check_result = await browser_manager.page.evaluate("""
                    () => {
                        // Check if results are available
                        if (window.botDetectionResults && typeof window.botDetectionResults === 'object') {
                            return {
                                hasResults: true,
                                isComplete: window.botDetectionResults.tests && window.botDetectionResults.tests.length > 0,
                                testsCount: window.botDetectionResults.tests ? window.botDetectionResults.tests.length : 0
                            };
                        }
                        
                        // Check scanner status and page content
                        const bodyText = document.body.innerText || '';
                        const windowKeys = Object.keys(window).filter(k => k.includes('bot') || k.includes('detection') || k.includes('scan'));
                        
                        return {
                            hasResults: false,
                            isComplete: false,
                            testsCount: 0,
                            isInitializing: bodyText.includes('Initializing'),
                            isScanning: bodyText.includes('Scanning') || bodyText.includes('Running'),
                            bodyPreview: bodyText.substring(0, 200),
                            windowKeys: windowKeys,
                            botDetectionType: typeof window.botDetectionResults,
                            url: window.location.href,
                            title: document.title
                        };
                    }
                """)
                
                if check_result['hasResults'] and check_result['isComplete']:
                    self._log(f"✅ Bot detection completed! Found {check_result['testsCount']} tests")
                    await asyncio.sleep(1)  # Final wait for completion
                    return
                    
                # Log detailed progress every 5 seconds
                if attempt % 5 == 0:
                    status = "initializing" if check_result.get('isInitializing') else ("scanning" if check_result.get('isScanning') else "unknown")
                    self._log(f"🔍 DEBUG Wait Status ({attempt}s):")
                    self._log(f"   URL: {check_result.get('url')}")
                    self._log(f"   Title: {check_result.get('title')}")
                    self._log(f"   Status: {status}")
                    self._log(f"   botDetectionResults type: {check_result.get('botDetectionType')}")
                    self._log(f"   Window keys: {check_result.get('windowKeys')}")
                    self._log(f"   Body preview: {check_result.get('bodyPreview')}")
                    
                await asyncio.sleep(1)
                attempt += 1
                    
            except Exception as e:
                self._log(f"⚠️ Error checking results: {e}", "warning")
                await asyncio.sleep(1)
                attempt += 1
        
        self._log("⚠️ Bot detection results not available after 45s timeout", "warning")

    async def _extract_bot_results(self, page: Page) -> Optional[BotDetectionResults]:
        """Extract and parse bot detection results"""
        try:
            # First, let's debug what's on the page
            debug_info = await page.evaluate("""
                () => {
                    return {
                        title: document.title,
                        url: window.location.href,
                        bodyText: document.body.innerText.substring(0, 200),
                        hasBotDetectionResults: typeof window.botDetectionResults !== 'undefined',
                        botDetectionResultsType: typeof window.botDetectionResults,
                        botDetectionResultsValue: window.botDetectionResults,
                        windowKeys: Object.keys(window).filter(k => k.includes('bot') || k.includes('detection')).slice(0, 10)
                    };
                }
            """)
            
            self._log(f"🔍 DEBUG Page Info:", "info")
            self._log(f"   Title: {debug_info.get('title')}", "info")
            self._log(f"   URL: {debug_info.get('url')}", "info")
            self._log(f"   Body preview: {debug_info.get('bodyText')}", "info")
            self._log(f"   Has botDetectionResults: {debug_info.get('hasBotDetectionResults')}", "info")
            self._log(f"   Type: {debug_info.get('botDetectionResultsType')}", "info")
            self._log(f"   Value: {debug_info.get('botDetectionResultsValue')}", "info")
            self._log(f"   Window keys: {debug_info.get('windowKeys')}", "info")
            
            # Extract results from window.botDetectionResults
            raw_results = await page.evaluate("""
                () => {
                    if (window.botDetectionResults) {
                        return window.botDetectionResults;
                    }
                    return null;
                }
            """)
            
            if not raw_results:
                self._log("⚠️ No botDetectionResults found", "warning")
                return None
                
            self._log(f"🔍 Raw results type: {type(raw_results)}, value: {raw_results}", "info")
                
            # Parse with Pydantic
            return BotDetectionResults(**raw_results)
            
        except Exception as e:
            self._log(f"❌ Failed to extract results: {e}", "error")
            return None

    def print_results(self, response: BotDetectionResponse) -> None:
        """Print formatted test results"""
        self._log("\n🔬 STEALTH TEST RESULTS", "info")
        self._log("=" * 50, "info")
        
        if not response.success:
            self._log(f"❌ Test failed: {response.error.error if response.error else 'Unknown error'}", "error")
            if response.scanner_url:
                self._log(f"🌐 Scanner: {response.scanner_url}", "info")
            if response.method:
                self._log(f"🥷 Method: {response.method}", "info")
            return
            
        if not response.results:
            self._log("❌ No results available", "error")
            return
            
        results = response.results
        
        # Basic info
        self._log(f"🌐 Scanner: {response.scanner_url or 'Unknown'}", "info")
        self._log(f"🥷 Method: {response.method or 'Unknown'}", "info")
        self._log(f"📊 Score: {results.overall_score}% | Bot: {results.is_bot} | Confidence: {results.confidence}", "info")
        self._log(f"📈 Tests: {results.summary.passed}✅ {results.summary.failed}❌ {results.summary.warnings}⚠️ ({results.summary.total} total)", "info")
        self._log(f"🏆 Effectiveness: {results.get_effectiveness_rating()}", "info")
        
        # Failed tests
        if results.failed_tests:
            self._log(f"\n❌ Failed Tests ({len(results.failed_tests)}):", "warning")
            for test in results.failed_tests[:3]:  # Show top 3
                self._log(f"   • {test.name}: {test.description} (Score: {test.score})", "warning")
        
        # Critical failures
        if results.critical_failures:
            self._log(f"\n🚨 Critical Failures ({len(results.critical_failures)}):", "error")
            for failure in results.critical_failures:
                self._log(f"   • {failure.name}: {failure.description}", "error")
        
        # Recommendations
        recommendations = results.get_recommendations()
        if recommendations:
            self._log(f"\n💡 Recommendations:", "info")
            for rec in recommendations[:3]:  # Show top 3
                self._log(f"   • {rec}", "info")

    def print_comparison(self, results: List[BotDetectionResponse]) -> None:
        """Print comparison results"""
        self._log("\n🔬 STEALTH METHOD COMPARISON", "info")
        self._log("=" * 60, "info")
        
        successful_results = [r for r in results if r.success and r.results]
        
        if not successful_results:
            self._log("❌ No successful tests to compare", "error")
            return
            
        # Sort by score (best first)
        successful_results.sort(key=lambda x: x.results.overall_score)
        best = successful_results[0]
        
        self._log(f"🏆 WINNER: {best.method} (Score: {best.results.overall_score}%)", "info")
        
        # Show all results
        for i, result in enumerate(results, 1):
            if result.success and result.results:
                r = result.results
                status = "🏆" if result == best else f"{i}."
                self._log(f"{status} {result.method}: {r.overall_score}% | Bot: {r.is_bot} | {r.get_effectiveness_rating()}", "info")
            else:
                self._log(f"{i}. {result.method}: ❌ Failed - {result.error.error if result.error else 'Unknown'}", "error")

    def get_best_method(self, results: List[BotDetectionResponse]) -> Optional[str]:
        """Get the best performing method from comparison results"""
        successful_results = [r for r in results if r.success and r.results]
        if not successful_results:
            return None
            
        best = min(successful_results, key=lambda x: x.results.overall_score)
        return best.method
