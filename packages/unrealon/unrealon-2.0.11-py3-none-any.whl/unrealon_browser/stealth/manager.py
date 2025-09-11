"""
StealthManager - Main manager for all detection bypass techniques

Coordinates work of all stealth modules:
- PlaywrightStealth for playwright-stealth integration
- UndetectedChrome for undetected-chromedriver
- NoDriverStealth for NoDriver
- BypassTechniques for advanced BotD bypass techniques
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from playwright.async_api import Page, BrowserContext

from unrealon_core.config.urls import get_url_config
from unrealon_browser.dto import BotDetectionResults, BotDetectionResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class StealthManager:
    """
    Main manager for all detection bypass techniques
    
    Coordinates application of various stealth techniques:
    - Playwright-stealth 2.0.0
    - Undetected ChromeDriver integration  
    - NoDriver support
    - Advanced BotD bypass techniques
    """

    def __init__(self, logger_bridge=None):
        """Initialize stealth manager"""
        self.stealth_applied = False
        self.test_results: Optional[Dict[str, Any]] = None
        self.logger_bridge = logger_bridge
        
        # Lazy import stealth modules to avoid circular imports
        self._playwright_stealth = None
        self._undetected_chrome = None
        self._nodriver_stealth = None
        self._bypass_techniques = None
        self._scanner_tester = None

    def _get_stealth_test_url(self) -> str:
        """Get stealth test URL from configuration."""
        return get_url_config().stealth_test_url

    def _logger(self, message: str, level: str = "info") -> None:
        """Private wrapper for logger with bridge support"""
        if self.logger_bridge:
            if level == "info":
                self.logger_bridge.log_info(message)
            elif level == "error":
                self.logger_bridge.log_error(message)
            elif level == "warning":
                self.logger_bridge.log_warning(message)
            else:
                self.logger_bridge.log_info(message)
        else:
            if level == "info":
                logger.info(message)
            elif level == "error":
                logger.error(message)
            elif level == "warning":
                logger.warning(message)
            else:
                logger.info(message)

    @property
    def playwright_stealth(self):
        """Lazy load PlaywrightStealth"""
        if self._playwright_stealth is None:
            from .playwright_stealth import PlaywrightStealth
            self._playwright_stealth = PlaywrightStealth(self.logger_bridge)
        return self._playwright_stealth

    @property
    def undetected_chrome(self):
        """Lazy load UndetectedChrome"""
        if self._undetected_chrome is None:
            from .undetected_chrome import UndetectedChrome
            self._undetected_chrome = UndetectedChrome(self.logger_bridge)
        return self._undetected_chrome

    @property
    def nodriver_stealth(self):
        """Lazy load NoDriverStealth"""
        if self._nodriver_stealth is None:
            from .nodriver_stealth import NoDriverStealth
            self._nodriver_stealth = NoDriverStealth(self.logger_bridge)
        return self._nodriver_stealth

    @property
    def bypass_techniques(self):
        """Lazy load BypassTechniques"""
        if self._bypass_techniques is None:
            from .bypass_techniques import BypassTechniques
            self._bypass_techniques = BypassTechniques(self.logger_bridge)
        return self._bypass_techniques

    @property
    def scanner_tester(self):
        """Lazy load ScannerTester"""
        if not hasattr(self, '_scanner_tester') or self._scanner_tester is None:
            from .scanner_tester import ScannerTester
            self._scanner_tester = ScannerTester(self.logger_bridge)
        return self._scanner_tester

    def get_stealth_args(self) -> List[str]:
        """
        Get comprehensive stealth arguments for browser launch
        Combines best practices from all stealth techniques
        """
        import platform
        
        args = [
            # 🔥 CRITICAL: Remove automation indicators
            "--disable-blink-features=AutomationControlled",
            "--disable-features=VizDisplayCompositor",
            
            # 🥷 Security & Detection Bypass
            "--disable-web-security",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--disable-client-side-phishing-detection",
            "--disable-component-extensions-with-background-pages",
            "--disable-default-apps",
            "--disable-domain-reliability",
            "--disable-background-networking",
            
            # 🎭 Mimic real user behavior
            "--no-first-run",
            "--no-default-browser-check", 
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-translate",
            
            # 📐 Window & Display - realistic settings
            "--window-size=1366,768",  # More common resolution
            "--start-maximized",
            "--hide-scrollbars",
            
            # ⚡ Performance & Background
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding", 
            "--disable-field-trial-config",
            "--disable-back-forward-cache",
            
            # 🔧 System & Monitoring
            "--disable-hang-monitor",
            "--disable-prompt-on-repost",
            "--disable-sync",
            "--metrics-recording-only",
            "--no-report-upload",
            "--mute-audio",
            
            # 🆕 Enhanced for BotD bypass (keep some extensions for realism)
            "--disable-extensions-except=",
        ]
        
        # 🍎 macOS specific fixes for "Mach rendezvous failed" error
        if platform.system() == "Darwin":
            args.extend([
                "--disable-gpu",  # Disable GPU acceleration on macOS
                "--disable-software-rasterizer",  # Disable software rasterizer
                "--disable-background-mode",  # Disable background mode
                "--disable-features=VizDisplayCompositor,VizHitTestSurfaceLayer",  # Disable problematic features
                "--use-gl=swiftshader",  # Use software GL implementation
                "--disable-ipc-flooding-protection",  # Disable IPC flooding protection
                "--single-process",  # Use single process mode to avoid IPC issues
            ])
        
        return args

    async def apply_stealth(self, page: Page, method: str = "comprehensive") -> bool:
        """
        Apply stealth measures to page
        
        Args:
            page: Playwright page instance
            method: Stealth method ("playwright", "comprehensive", "aggressive")
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self._logger(f"🥷 Applying stealth measures (method: {method})...", "info")

            success = True

            if method in ["playwright", "comprehensive"]:
                # 1. Apply playwright-stealth 2.0.0
                playwright_success = await self.playwright_stealth.apply_stealth(page)
                success = success and playwright_success

            if method in ["comprehensive", "aggressive"]:
                # 2. Apply advanced BotD bypass techniques
                bypass_success = await self.bypass_techniques.apply_all_bypasses(page)
                success = success and bypass_success

            # 3. Always apply basic webdriver removal
            await self.bypass_techniques.apply_webdriver_removal(page)

            self.stealth_applied = success
            
            if success:
                self._logger("✅ Stealth measures applied successfully", "info")
            else:
                self._logger("⚠️ Some stealth measures failed, but continuing", "warning")

            return success

        except Exception as e:
            self._logger(f"❌ Failed to apply stealth measures: {e}", "error")
            self.stealth_applied = False
            return False

    async def apply_stealth_to_context(self, context: BrowserContext) -> bool:
        """Apply stealth measures to entire browser context"""
        try:
            self._logger("🥷 Applying stealth to browser context...", "info")

            # Apply context-level stealth scripts
            success = await self.bypass_techniques.apply_context_stealth(context)
            
            if success:
                self._logger("✅ Context stealth applied successfully", "info")
            else:
                self._logger("⚠️ Context stealth partially failed", "warning")

            return success

        except Exception as e:
            self._logger(f"❌ Failed to apply context stealth: {e}", "error")
            return False

    async def apply_webdriver_removal(self, context: BrowserContext) -> bool:
        """
        Apply webdriver removal to browser context
        
        Args:
            context: Playwright browser context
            
        Returns:
            True if successful
        """
        try:
            self._logger("🛡️ Applying webdriver removal to context...", "info")
            
            # Use bypass techniques for webdriver removal
            success = await self.bypass_techniques.apply_context_stealth(context)
            
            if success:
                self._logger("✅ Webdriver removal applied successfully", "info")
            else:
                self._logger("⚠️ Webdriver removal partially failed", "warning")
                
            return success
            
        except Exception as e:
            self._logger(f"❌ Failed to apply webdriver removal: {e}", "error")
            return False

    async def test_stealth_effectiveness(self, browser_manager) -> Dict[str, Any]:
        """
        Test stealth effectiveness using ScannerTester
        
        Args:
            browser_manager: Browser manager instance with page
            
        Returns:
            Dict with test results and detection metrics
        """
        self._logger("🔍 DEBUG: test_stealth_effectiveness called", "info")
        self._logger(f"🔍 DEBUG: browser_manager={browser_manager}, page={browser_manager.page if browser_manager else None}", "info")
        
        if not browser_manager or not browser_manager.page:
            self._logger("❌ DEBUG: Browser manager or page not available", "error")
            return {
                "success": False,
                "error": "Browser manager or page not available",
                "skipped": True,
            }

        try:
            self._logger("🧪 Testing stealth effectiveness using ScannerTester...", "info")
            self._logger("🔍 DEBUG: About to call scanner_tester.test_stealth()", "info")
            
            # Use ScannerTester for proper testing
            response = await self.scanner_tester.test_stealth(browser_manager, self, "comprehensive")
            
            self._logger(f"🔍 DEBUG: scanner_tester.test_stealth() returned: {response}", "info")
            
            # Convert BotDetectionResponse to dict format for compatibility
            if response.success and response.results:
                results = response.results
                
                # Store results for later access
                self.test_results = results.model_dump()
                
                return {
                    "success": True,
                    "results": results.model_dump(),
                    "detection_score": results.overall_score,
                    "is_bot": results.is_bot,
                    "confidence": results.confidence,
                    "tests_passed": results.summary.passed,
                    "tests_failed": results.summary.failed,
                    "total_tests": results.summary.total,
                    "error": None,
                    "skipped": False,
                }
            else:
                error_msg = response.error.error if response.error else "Unknown scanner error"
                return {
                    "success": False,
                    "error": error_msg,
                    "skipped": False,
                }

        except Exception as e:
            self._logger(f"❌ Stealth test failed: {e}", "error")
            return {
                "success": False,
                "error": str(e),
                "skipped": False,
            }

    def get_stealth_status(self) -> Dict[str, Any]:
        """Get current stealth status and test results"""
        return {
            "stealth_applied": self.stealth_applied,
            "test_results": self.test_results,
        }

    def print_stealth_status(self) -> None:
        """Print current stealth status"""
        status = self.get_stealth_status()

        self._logger("\n🥷 Stealth Status:", "info")
        self._logger(f"Applied: {status['stealth_applied']}", "info")

        if status["test_results"]:
            results = status["test_results"]
            self._logger(f"   Last test score: {results.get('detection_score', 'Unknown')}", "info")
            self._logger(f"Tests passed: {results.get('tests_passed', 0)}/{results.get('total_tests', 0)}")

    async def test_with_scanner(self, browser_manager, method: str = "comprehensive") -> Dict[str, Any]:
        """
        Convenient method to test stealth effectiveness with our scanner
        
        Args:
            browser_manager: Browser manager instance
            method: Stealth method to test ("playwright", "comprehensive", "aggressive")
            
        Returns:
            Dict with test results from our scanner
        """
        self._logger(f"🔬 Testing stealth with UnrealOn scanner (method: {method})", "info")
        
        try:
            # Apply stealth first
            if browser_manager.page:
                stealth_applied = await self.apply_stealth(browser_manager.page, method)
                self._logger(f"🥷 Stealth applied: {stealth_applied}", "info")
            
            # Use the existing test_stealth_effectiveness method
            result = await self.test_stealth_effectiveness(browser_manager)
            
            # Debug: Check result type (force print)
            self._logger(f"🔍 test_stealth_effectiveness result type: {type(result)}, value: {result}", "info")
            
            # Store results and add method info
            if isinstance(result, dict) and result.get("success"):
                result["method"] = method
                result["test_type"] = "scanner_test"
                
                # Log summary
                self._logger(f"📊 Scanner Results ({method}):", "info")
                self._logger(f"   Detection Score: {result.get('detection_score', 'N/A')}%", "info")
                self._logger(f"   Bot Detected: {result.get('is_bot', 'N/A')}", "info")
                self._logger(f"   Confidence: {result.get('confidence', 'N/A')}", "info")
                self._logger(f"   Tests Passed: {result.get('tests_passed', 0)}/{result.get('total_tests', 0)}", "info")
                
                # Show failed tests if any
                if result.get("results") and "tests" in result["results"]:
                    failed_tests = [test for test in result["results"]["tests"] if test.get("status") == "failed"]
                    if failed_tests:
                        self._logger(f"   ⚠️ Failed Tests: {len(failed_tests)}", "warning")
                        for test in failed_tests[:3]:  # Show first 3
                            self._logger(f"      • {test.get('name', 'Unknown')}", "warning")
            
            return result
            
        except Exception as e:
            self._logger(f"❌ Scanner test failed: {e}", "error")
            return {
                "success": False,
                "error": str(e),
                "method": method
            }

    async def test_all_methods_with_scanner(self, browser_manager) -> Dict[str, Any]:
        """
        Test all stealth methods with our scanner and compare results
        
        Args:
            browser_manager: Browser manager instance
            
        Returns:
            Dict with comprehensive comparison results
        """
        self._logger("🔬 Testing all stealth methods with UnrealOn scanner", "info")
        
        try:
            # Use scanner tester for comprehensive test
            results = await self.scanner_tester.test_stealth_comprehensive(browser_manager, self)
            
            # Print formatted results
            self.scanner_tester.print_test_results(results)
            
            # Store best results
            if results.get("best_config"):
                self.test_results = results["best_config"].get("raw_results", results["best_config"])
            
            return results
            
        except Exception as e:
            self._logger(f"❌ Comprehensive scanner test failed: {e}", "error")
            return {
                "success": False,
                "error": str(e),
                "test_type": "comprehensive"
            }

    async def compare_stealth_methods_with_scanner(self, browser_manager) -> Dict[str, Any]:
        """
        Compare different stealth methods using our scanner
        
        Args:
            browser_manager: Browser manager instance
            
        Returns:
            Dict with comparison results
        """
        self._logger("🔬 Comparing stealth methods with UnrealOn scanner", "info")
        
        try:
            # Use scanner tester for comparison
            results = await self.scanner_tester.test_stealth_comparison(browser_manager, self)
            
            # Print formatted results
            self.scanner_tester.print_test_results(results)
            
            # Store winner results
            if results.get("winner"):
                self.test_results = results["winner"].get("raw_results", results["winner"])
            
            return results
            
        except Exception as e:
            self._logger(f"❌ Scanner comparison test failed: {e}", "error")
            return {
                "success": False,
                "error": str(e),
                "test_type": "comparison"
            }

    def get_scanner_recommendations(self) -> List[str]:
        """
        Get recommendations based on last scanner test results
        
        Returns:
            List of recommendations for improving stealth
        """
        if not self.test_results:
            return ["Run scanner test first to get recommendations"]
        
        # Extract recommendations from test results
        if isinstance(self.test_results, dict):
            # Check if it's a comprehensive result with analysis
            if "analysis" in self.test_results:
                return self.test_results["analysis"].get("recommendations", [])
            
            # Check if it's raw bot detection results
            if "tests" in self.test_results:
                recommendations = []
                failed_tests = [test for test in self.test_results.get("tests", []) if test.get("status") == "failed"]
                
                # Generate basic recommendations based on failed tests
                for test in failed_tests:
                    test_name = test.get("name", "")
                    if "BotD" in test_name:
                        recommendations.append("Consider using headed mode for better BotD bypass")
                    elif "WebDriver" in test_name:
                        recommendations.append("Enhance webdriver property removal")
                    elif "Chrome Object" in test_name:
                        recommendations.append("Improve window.chrome object spoofing")
                    elif "Plugin" in test_name:
                        recommendations.append("Add more realistic browser plugins")
                
                return recommendations[:5]  # Limit to 5 recommendations
        
        return ["No specific recommendations available"]
