"""
PlaywrightStealth - Integration with playwright-stealth 2.0.0

Provides integration with playwright-stealth library for detection bypass:
- Configuration of all available stealth options
- Application to pages and contexts
- Error handling and fallback
"""

import logging
from playwright.async_api import Page, BrowserContext

# CRITICAL REQUIREMENTS COMPLIANCE - NO INLINE IMPORTS!
from playwright_stealth import Stealth

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class PlaywrightStealth:
    """
    Integration with playwright-stealth 2.0.0
    
    Provides application of all available stealth techniques
    from playwright-stealth library for maximum detection bypass
    """

    def __init__(self, logger_bridge=None):
        """Initialize PlaywrightStealth"""
        self.logger_bridge = logger_bridge
        self.stealth_config = self._create_stealth_config()

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

    def _create_stealth_config(self) -> Stealth:
        """
        Create comprehensive stealth configuration
        Enables ALL available stealth features for maximum protection
        """
        return Stealth(
            # 🔥 CRITICAL: Core webdriver removal
            navigator_webdriver=True,  # Remove navigator.webdriver property
            
            # 🎭 Chrome object spoofing
            chrome_runtime=True,  # Enable chrome runtime spoofing
            chrome_app=True,  # Enable chrome app spoofing
            chrome_csi=True,  # Enable chrome CSI spoofing
            chrome_load_times=True,  # Enable load times spoofing
            
            # 🌐 Navigator spoofing
            navigator_languages=True,  # Spoof languages
            navigator_permissions=True,  # Spoof permissions
            navigator_plugins=True,  # Spoof plugins
            navigator_user_agent=True,  # Spoof user agent - CRITICAL for headless
            navigator_vendor=True,  # Spoof navigator vendor
            navigator_platform=True,  # Spoof platform
            navigator_hardware_concurrency=True,  # Spoof hardware concurrency
            
            # 🎨 WebGL and Canvas spoofing
            webgl_vendor=True,  # Spoof WebGL vendor - CRITICAL for BotD
            hairline=True,  # Enable hairline spoofing - helps with canvas fingerprinting
            
            # 🔧 Modern browser features
            sec_ch_ua=True,  # Enable sec-ch-ua spoofing - modern Chrome headers
            iframe_content_window=True,  # Enable iframe spoofing
            media_codecs=True,  # Enable media codecs spoofing
        )

    async def apply_stealth(self, page: Page) -> bool:
        """
        Apply playwright-stealth to page
        
        Args:
            page: Playwright page instance
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._logger("🎭 Applying playwright-stealth 2.0.0...", "info")
            
            # Apply stealth using new 2.0.0 API
            await self.stealth_config.apply_stealth_async(page)
            
            self._logger("✅ Playwright-stealth 2.0.0 applied successfully", "info")
            return True
            
        except Exception as e:
            self._logger(f"❌ Playwright-stealth failed: {e}", "error")
            return False

    async def apply_stealth_to_context(self, context: BrowserContext) -> bool:
        """
        Apply stealth to browser context
        
        Args:
            context: Playwright browser context
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._logger("🎭 Applying playwright-stealth to context...", "info")
            
            # For context, we need to apply stealth to each new page
            # This is handled by the context's page creation events
            
            # Add init script for basic webdriver removal at context level
            webdriver_removal_script = """
            // Basic webdriver removal at context level
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
                configurable: true
            });
            
            // Remove from prototype
            if (navigator.webdriver !== undefined) {
                delete Object.getPrototypeOf(navigator).webdriver;
            }
            """
            
            await context.add_init_script(webdriver_removal_script)
            
            self._logger("✅ Playwright-stealth context setup completed", "info")
            return True
            
        except Exception as e:
            self._logger(f"❌ Playwright-stealth context setup failed: {e}", "error")
            return False

    def get_stealth_info(self) -> dict:
        """
        Get information about current stealth configuration
        
        Returns:
            Dict with stealth configuration details
        """
        return {
            "library": "playwright-stealth",
            "version": "2.0.0",
            "features_enabled": {
                "navigator_webdriver": True,
                "chrome_runtime": True,
                "chrome_app": True,
                "chrome_csi": True,
                "chrome_load_times": True,
                "navigator_languages": True,
                "navigator_permissions": True,
                "navigator_plugins": True,
                "navigator_user_agent": True,
                "navigator_vendor": True,
                "navigator_platform": True,
                "navigator_hardware_concurrency": True,
                "webgl_vendor": True,
                "hairline": True,
                "sec_ch_ua": True,
                "iframe_content_window": True,
                "media_codecs": True,
            },
            "description": "Comprehensive stealth configuration with all features enabled"
        }
