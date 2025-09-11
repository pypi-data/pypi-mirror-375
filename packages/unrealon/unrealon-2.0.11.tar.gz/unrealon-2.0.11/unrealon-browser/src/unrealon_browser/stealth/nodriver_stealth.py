"""
NoDriverStealth - Integration with NoDriver

Provides integration with NoDriver for next-generation bot detection bypass:
- Async-first architecture
- No external ChromeDriver dependency
- Built-in stealth capabilities
- Advanced BotD bypass
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class NoDriverStealth:
    """
    Integration with NoDriver
    
    NoDriver is the next-generation successor to undetected-chromedriver
    with async-first architecture and built-in stealth capabilities
    """

    def __init__(self, logger_bridge=None):
        """Initialize NoDriverStealth"""
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

    def get_nodriver_config(self) -> Dict[str, Any]:
        """
        Get optimized configuration for NoDriver
        
        Returns:
            Dict with NoDriver configuration
        """
        return {
            "headless": False,  # Recommend headed for best stealth
            "browser_args": self.get_nodriver_arguments(),
            "user_data_dir": None,  # Use temporary profile
            "lang": "en-US",
            "sandbox": False,
            "incognito": False,  # Regular mode for better stealth
            "host": "localhost",
            "port": 0,  # Auto-assign port
        }

    def get_nodriver_arguments(self) -> List[str]:
        """
        Get optimized browser arguments for NoDriver
        
        Returns:
            List of browser arguments for maximum stealth
        """
        return [
            # Core stealth arguments
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=VizDisplayCompositor",
            
            # Enhanced stealth for NoDriver
            "--disable-web-security",
            "--disable-client-side-phishing-detection",
            "--disable-component-extensions-with-background-pages",
            "--disable-default-apps",
            "--disable-domain-reliability",
            "--disable-background-networking",
            "--disable-translate",
            "--disable-ipc-flooding-protection",
            
            # Performance optimization
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
            
            # Window and display
            "--window-size=1366,768",
            "--start-maximized",
            
            # Media settings
            "--mute-audio",
            "--disable-audio-output",
            
            # Extensions (minimal for realism)
            "--disable-extensions-except=",
            
            # Memory optimization
            "--max_old_space_size=4096",
            "--memory-pressure-off",
            
            # Additional NoDriver optimizations
            "--disable-logging",
            "--disable-gpu-logging",
            "--silent",
        ]

    async def create_nodriver_browser(self, **kwargs) -> Optional[Any]:
        """
        Create NoDriver browser instance
        
        Args:
            **kwargs: Additional configuration options
            
        Returns:
            NoDriver browser instance or None if failed
        """
        try:
            import nodriver as uc
            
            self._logger("🚀 Creating NoDriver browser...", "info")
            
            # Get base configuration
            config = self.get_nodriver_config()
            config.update(kwargs)
            
            # Create browser
            browser = await uc.start(**config)
            
            # Apply additional stealth measures
            await self.apply_nodriver_stealth(browser)
            
            self._logger("✅ NoDriver browser created successfully", "info")
            return browser
            
        except ImportError as e:
            self._logger(f"❌ NoDriver not available: {e}", "error")
            return None
        except Exception as e:
            self._logger(f"❌ Failed to create NoDriver browser: {e}", "error")
            return None

    async def apply_nodriver_stealth(self, browser) -> bool:
        """
        Apply additional stealth measures to NoDriver browser
        
        Args:
            browser: NoDriver browser instance
            
        Returns:
            True if successful
        """
        try:
            self._logger("🛡️ Applying NoDriver stealth measures...", "info")
            
            # Get the main tab/page
            page = await browser.get("about:blank")
            
            # Apply comprehensive stealth scripts
            await self.apply_stealth_scripts(page)
            
            self._logger("✅ NoDriver stealth measures applied", "info")
            return True
            
        except Exception as e:
            self._logger(f"❌ Failed to apply NoDriver stealth: {e}", "error")
            return False

    async def apply_stealth_scripts(self, page) -> None:
        """
        Apply comprehensive stealth scripts to NoDriver page
        
        Args:
            page: NoDriver page instance
        """
        # Enhanced webdriver removal
        webdriver_script = """
        // Comprehensive webdriver removal for NoDriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
            configurable: true
        });
        
        // Remove from prototype
        if (navigator.webdriver !== undefined) {
            delete Object.getPrototypeOf(navigator).webdriver;
        }
        
        // Remove automation indicators
        ['__webdriver_evaluate', '__selenium_evaluate', '__webdriver_script_function',
         '__fxdriver_evaluate', '__driver_unwrapped', '__webdriver_unwrapped',
         '_Selenium_IDE_Recorder', '_selenium', 'calledSelenium',
         '_WEBDRIVER_ELEM_CACHE', 'ChromeDriverw', '$cdc_asdjflasutopfhvcZLmcfl_'].forEach(prop => {
            delete window[prop];
            delete document[prop];
        });
        """
        
        # Chrome object creation
        chrome_script = """
        // Create realistic Chrome object for NoDriver
        if (!window.chrome) {
            window.chrome = {
                runtime: {
                    onConnect: null,
                    onMessage: null,
                    sendMessage: () => {},
                    connect: () => ({
                        onMessage: { addListener: () => {}, removeListener: () => {} },
                        onDisconnect: { addListener: () => {}, removeListener: () => {} },
                        postMessage: () => {}
                    }),
                    id: undefined
                },
                app: {
                    isInstalled: false
                },
                csi: () => {},
                loadTimes: () => ({
                    requestTime: Date.now() / 1000,
                    startLoadTime: Date.now() / 1000,
                    commitLoadTime: Date.now() / 1000,
                    finishDocumentLoadTime: Date.now() / 1000,
                    finishLoadTime: Date.now() / 1000,
                    firstPaintTime: Date.now() / 1000,
                    firstPaintAfterLoadTime: 0,
                    navigationType: 'Other'
                })
            };
        }
        """
        
        # Plugin spoofing
        plugin_script = """
        // Plugin spoofing for NoDriver
        const plugins = [
            {
                name: 'Chrome PDF Plugin',
                filename: 'internal-pdf-viewer',
                description: 'Portable Document Format',
                length: 1
            },
            {
                name: 'Chrome PDF Viewer',
                filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                description: 'Portable Document Format',
                length: 1
            }
        ];
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => plugins,
            configurable: true
        });
        """
        
        # WebGL spoofing
        webgl_script = """
        // WebGL spoofing for NoDriver
        const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Intel Inc.';
            if (parameter === 37446) return 'Intel Iris OpenGL Engine';
            return originalGetParameter.call(this, parameter);
        };
        """
        
        # Apply all scripts
        scripts = [webdriver_script, chrome_script, plugin_script, webgl_script]
        
        for script in scripts:
            try:
                await page.evaluate(script)
            except Exception as e:
                self._logger(f"⚠️ Script application warning: {e}", "warning")

    async def test_nodriver_stealth(self, test_url: str) -> Dict[str, Any]:
        """
        Test NoDriver stealth effectiveness
        
        Args:
            test_url: URL to test stealth effectiveness
            
        Returns:
            Dict with test results
        """
        browser = None
        try:
            self._logger(f"🧪 Testing NoDriver stealth on {test_url}...", "info")
            
            # Create browser
            browser = await self.create_nodriver_browser(headless=True)
            if not browser:
                return {
                    "success": False,
                    "error": "Failed to create NoDriver browser"
                }
            
            # Navigate to test page
            page = await browser.get(test_url)
            
            # Wait for page to load
            await asyncio.sleep(5)
            
            # Extract detection results
            try:
                results = await page.evaluate("""
                    () => {
                        return {
                            userAgent: navigator.userAgent,
                            webdriver: navigator.webdriver !== undefined,
                            chrome: !!window.chrome,
                            plugins: navigator.plugins.length,
                            languages: navigator.languages ? navigator.languages.length : 0,
                            botDetectionResults: window.botDetectionResults || null
                        };
                    }
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
            self._logger(f"❌ NoDriver test failed: {e}", "error")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            if browser:
                try:
                    browser.stop()
                except:
                    pass

    async def create_stealth_page(self, browser, url: str):
        """
        Create a new page with full stealth applied
        
        Args:
            browser: NoDriver browser instance
            url: URL to navigate to
            
        Returns:
            NoDriver page with stealth applied
        """
        try:
            # Create new page
            page = await browser.get(url)
            
            # Apply stealth scripts
            await self.apply_stealth_scripts(page)
            
            return page
            
        except Exception as e:
            self._logger(f"❌ Failed to create stealth page: {e}", "error")
            return None

    def get_stealth_info(self) -> Dict[str, Any]:
        """
        Get information about NoDriver capabilities
        
        Returns:
            Dict with capability information
        """
        return {
            "library": "nodriver",
            "architecture": "async-first",
            "features": {
                "no_external_chromedriver": True,
                "built_in_stealth": True,
                "async_operations": True,
                "devtools_protocol": True,
                "automatic_updates": True,
                "headless_support": True,
                "headed_mode_recommended": True,
                "memory_efficient": True
            },
            "bypass_capabilities": {
                "cloudflare": True,
                "datadome": True,
                "imperva": True,
                "botd": "advanced",
                "recaptcha": True,
                "advanced_fingerprinting": True,
                "waf_bypass": True
            },
            "advantages": [
                "No ChromeDriver dependency",
                "Better performance with async operations",
                "Built-in stealth capabilities",
                "Regular updates and maintenance",
                "Advanced DevTools Protocol usage"
            ],
            "description": "Next-generation bot detection bypass with async architecture"
        }
