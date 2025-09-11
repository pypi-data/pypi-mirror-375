"""
UndetectedChrome - Integration with undetected-chromedriver

Provides integration with undetected-chromedriver for advanced bot detection bypass:
- Automatic ChromeDriver patching
- Selenium stealth integration
- Advanced Chrome arguments
- BotD bypass optimization
"""

import logging
from typing import Dict, Any, Optional, List
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class UndetectedChrome:
    """
    Integration with undetected-chromedriver
    
    Provides seamless integration with undetected-chromedriver
    for maximum bot detection bypass effectiveness
    """

    def __init__(self, logger_bridge=None):
        """Initialize UndetectedChrome"""
        self.logger_bridge = logger_bridge

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

    def get_undetected_chrome_options(self) -> Dict[str, Any]:
        """
        Get optimized options for undetected-chromedriver
        
        Returns:
            Dict with Chrome options optimized for stealth
        """
        return {
            "headless": False,  # Recommend headed mode for best results
            "use_subprocess": False,
            "version_main": None,  # Auto-detect Chrome version
            "driver_executable_path": None,  # Auto-download
            "browser_executable_path": None,  # Use system Chrome
            "user_data_dir": None,  # Use temporary profile
            "suppress_welcome": True,
            "no_sandbox": True,
            "disable_gpu": False,  # Keep GPU for WebGL consistency
            "log_level": 3,  # Suppress logs
        }

    def get_enhanced_chrome_arguments(self) -> List[str]:
        """
        Get enhanced Chrome arguments for undetected-chromedriver
        
        Returns:
            List of Chrome arguments optimized for stealth
        """
        return [
            # Core stealth arguments
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=VizDisplayCompositor",
            
            # Enhanced stealth for BotD bypass
            "--disable-web-security",
            "--disable-client-side-phishing-detection",
            "--disable-component-extensions-with-background-pages",
            "--disable-default-apps",
            "--disable-domain-reliability",
            "--disable-background-networking",
            "--disable-translate",
            "--disable-ipc-flooding-protection",
            
            # Performance and stability
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-field-trial-config",
            "--disable-back-forward-cache",
            
            # System integration
            "--disable-hang-monitor",
            "--disable-prompt-on-repost",
            "--disable-sync",
            "--metrics-recording-only",
            "--no-report-upload",
            
            # Realistic window settings
            "--window-size=1366,768",
            "--start-maximized",
            
            # Audio and media
            "--mute-audio",
            "--disable-audio-output",
            
            # Extensions (keep minimal for realism)
            "--disable-extensions-except=",
            
            # Memory and performance
            "--max_old_space_size=4096",
            "--memory-pressure-off",
        ]

    def get_random_user_agent(self) -> str:
        """
        Get random realistic user agent
        
        Returns:
            Random user agent string
        """
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        return random.choice(user_agents)

    def create_undetected_driver(self, headless: bool = False, **kwargs) -> Any:
        """
        Create undetected ChromeDriver instance
        
        Args:
            headless: Whether to run in headless mode
            **kwargs: Additional options for undetected_chromedriver
            
        Returns:
            Configured undetected ChromeDriver instance
        """
        try:
            import undetected_chromedriver as uc
            from selenium_stealth import stealth
            
            self._logger("🚗 Creating undetected ChromeDriver...", "info")
            
            # Get base options
            options = self.get_undetected_chrome_options()
            options.update(kwargs)
            options["headless"] = headless
            
            # Create Chrome options
            chrome_options = uc.ChromeOptions()
            
            # Add enhanced arguments
            for arg in self.get_enhanced_chrome_arguments():
                chrome_options.add_argument(arg)
            
            # Add random user agent
            user_agent = self.get_random_user_agent()
            chrome_options.add_argument(f'--user-agent={user_agent}')
            
            # Disable automation indicators
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Create driver
            driver = uc.Chrome(options=chrome_options, **options)
            
            # Apply selenium-stealth
            stealth(
                driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            
            # Remove webdriver property
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            self._logger("✅ Undetected ChromeDriver created successfully", "info")
            return driver
            
        except ImportError as e:
            self._logger(f"❌ undetected-chromedriver not available: {e}", "error")
            return None
        except Exception as e:
            self._logger(f"❌ Failed to create undetected ChromeDriver: {e}", "error")
            return None

    def apply_selenium_stealth(self, driver) -> bool:
        """
        Apply selenium-stealth to existing driver
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            True if successful
        """
        try:
            from selenium_stealth import stealth
            
            self._logger("🛡️ Applying selenium-stealth...", "info")
            
            stealth(
                driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            
            # Additional webdriver removal
            driver.execute_script("""
                // Enhanced webdriver removal
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Remove automation indicators
                ['__webdriver_evaluate', '__selenium_evaluate', '__webdriver_script_function',
                 '__fxdriver_evaluate', '__driver_unwrapped', '__webdriver_unwrapped',
                 '_Selenium_IDE_Recorder', '_selenium', 'calledSelenium'].forEach(prop => {
                    delete window[prop];
                });
            """)
            
            self._logger("✅ Selenium-stealth applied successfully", "info")
            return True
            
        except ImportError as e:
            self._logger(f"❌ selenium-stealth not available: {e}", "error")
            return False
        except Exception as e:
            self._logger(f"❌ Failed to apply selenium-stealth: {e}", "error")
            return False

    def test_undetected_chrome(self, test_url: str) -> Dict[str, Any]:
        """
        Test undetected ChromeDriver effectiveness
        
        Args:
            test_url: URL to test stealth effectiveness
            
        Returns:
            Dict with test results
        """
        driver = None
        try:
            self._logger(f"🧪 Testing undetected ChromeDriver on {test_url}...", "info")
            
            # Create driver
            driver = self.create_undetected_driver(headless=True)
            if not driver:
                return {
                    "success": False,
                    "error": "Failed to create undetected ChromeDriver"
                }
            
            # Navigate to test page
            driver.get(test_url)
            
            # Wait for page to load
            import time
            time.sleep(5)
            
            # Extract basic detection info
            try:
                results = driver.execute_script("""
                    return {
                        userAgent: navigator.userAgent,
                        webdriver: navigator.webdriver !== undefined,
                        chrome: !!window.chrome,
                        plugins: navigator.plugins.length,
                        languages: navigator.languages ? navigator.languages.length : 0,
                        botDetectionResults: window.botDetectionResults || null
                    };
                """)
                
                return {
                    "success": True,
                    "results": results,
                    "is_bot": results.get("webdriver", False),
                    "user_agent": results.get("userAgent", ""),
                    "chrome_object": results.get("chrome", False),
                    "plugins_count": results.get("plugins", 0),
                    "bot_detection": results.get("botDetectionResults")
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to extract results: {e}"
                }
                
        except Exception as e:
            self._logger(f"❌ Undetected Chrome test failed: {e}", "error")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    def get_stealth_info(self) -> Dict[str, Any]:
        """
        Get information about undetected-chromedriver capabilities
        
        Returns:
            Dict with capability information
        """
        return {
            "library": "undetected-chromedriver",
            "selenium_stealth": "selenium-stealth",
            "features": {
                "automatic_chromedriver_patching": True,
                "webdriver_property_removal": True,
                "user_agent_spoofing": True,
                "chrome_arguments_optimization": True,
                "selenium_stealth_integration": True,
                "random_user_agents": True,
                "headless_support": True,
                "headed_mode_recommended": True
            },
            "bypass_capabilities": {
                "cloudflare": True,
                "datadome": True,
                "imperva": True,
                "botd": "partial",
                "recaptcha": True,
                "basic_detection": True
            },
            "description": "Most effective solution for Selenium-based bot detection bypass"
        }
