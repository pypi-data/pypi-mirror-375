"""
BypassTechniques - Advanced BotD bypass techniques

Implements cutting-edge techniques to bypass modern bot detection systems:
- BotD detection bypass (headless_chrome)
- Chrome Object Consistency fixes
- Permissions API spoofing
- Browser Plugins simulation
- WebGL Capabilities spoofing
- Advanced fingerprinting prevention
"""

import logging
from playwright.async_api import Page, BrowserContext

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class BypassTechniques:
    """
    Advanced BotD bypass techniques
    
    Implements state-of-the-art methods to bypass modern bot detection:
    - Headless Chrome detection bypass
    - Chrome object consistency
    - Permissions API spoofing
    - Plugin simulation
    - WebGL fingerprinting prevention
    """

    def __init__(self, logger_bridge=None):
        """Initialize BypassTechniques"""
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

    async def apply_all_bypasses(self, page: Page) -> bool:
        """
        Apply all bypass techniques to page
        
        Args:
            page: Playwright page instance
            
        Returns:
            True if all techniques applied successfully
        """
        try:
            self._logger("🛡️ Applying advanced BotD bypass techniques...", "info")
            
            success = True
            
            # Apply all bypass techniques
            techniques = [
                ("Headless Detection Bypass", self.apply_headless_detection_bypass),
                ("Chrome Object Consistency", self.apply_chrome_object_bypass),
                ("Permissions API Bypass", self.apply_permissions_bypass),
                ("Browser Plugins Bypass", self.apply_plugins_bypass),
                ("WebGL Capabilities Bypass", self.apply_webgl_bypass),
                ("Canvas Fingerprinting Bypass", self.apply_canvas_bypass),
                ("Timing Attack Prevention", self.apply_timing_bypass),
                ("User Agent Spoofing", self.apply_user_agent_bypass),
                ("Platform Spoofing", self.apply_platform_bypass),
            ]
            
            for name, technique in techniques:
                try:
                    await technique(page)
                    self._logger(f"✅ {name} applied", "info")
                except Exception as e:
                    self._logger(f"❌ {name} failed: {e}", "error")
                    success = False
            
            if success:
                self._logger("✅ All bypass techniques applied successfully", "info")
            else:
                self._logger("⚠️ Some bypass techniques failed", "warning")
                
            return success
            
        except Exception as e:
            self._logger(f"❌ Failed to apply bypass techniques: {e}", "error")
            return False

    async def apply_headless_detection_bypass(self, page: Page) -> None:
        """
        PROBLEM 1: BotD Detection (headless_chrome) - CRITICAL FIX
        """
        script = """
        // 1. Remove headless indicators from User Agent
        const originalUserAgent = navigator.userAgent;
        Object.defineProperty(navigator, 'userAgent', {
            get: () => originalUserAgent
                .replace(/HeadlessChrome/g, 'Chrome')
                .replace(/headless/gi, ''),
            configurable: true
        });
        
        // 2. Spoof window.outerWidth/outerHeight (headless = 0)
        Object.defineProperty(window, 'outerWidth', { 
            get: () => 1366,
            configurable: true 
        });
        Object.defineProperty(window, 'outerHeight', { 
            get: () => 768,
            configurable: true 
        });
        
        // 3. Add missing window properties that headless lacks
        if (!window.screenX) {
            Object.defineProperty(window, 'screenX', { 
                get: () => 0,
                configurable: true 
            });
        }
        if (!window.screenY) {
            Object.defineProperty(window, 'screenY', { 
                get: () => 0,
                configurable: true 
            });
        }
        
        // 4. Fix window.screen properties
        Object.defineProperty(window.screen, 'availLeft', { 
            get: () => 0,
            configurable: true 
        });
        Object.defineProperty(window.screen, 'availTop', { 
            get: () => 0,
            configurable: true 
        });
        """
        await page.add_init_script(script)

    async def apply_chrome_object_bypass(self, page: Page) -> None:
        """
        PROBLEM 2: Chrome Object Consistency - CREATE REALISTIC CHROME
        """
        script = """
        // Create comprehensive window.chrome object
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
                    isInstalled: false,
                    InstallState: { 
                        DISABLED: 'disabled', 
                        INSTALLED: 'installed', 
                        NOT_INSTALLED: 'not_installed' 
                    },
                    RunningState: { 
                        CANNOT_RUN: 'cannot_run', 
                        READY_TO_RUN: 'ready_to_run', 
                        RUNNING: 'running' 
                    }
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
                    navigationType: 'Other',
                    wasFetchedViaSpdy: false,
                    wasNpnNegotiated: false,
                    npnNegotiatedProtocol: 'unknown',
                    wasAlternateProtocolAvailable: false,
                    connectionInfo: 'http/1.1'
                }),
                storage: {
                    local: {
                        get: function(callback) { if (callback) callback({}); },
                        set: function(items, callback) { if (callback) callback(); },
                        remove: function(keys, callback) { if (callback) callback(); },
                        clear: function(callback) { if (callback) callback(); }
                    },
                    sync: {
                        get: function(callback) { if (callback) callback({}); },
                        set: function(items, callback) { if (callback) callback(); },
                        remove: function(keys, callback) { if (callback) callback(); },
                        clear: function(callback) { if (callback) callback(); }
                    }
                }
            };
        }
        """
        await page.add_init_script(script)

    async def apply_permissions_bypass(self, page: Page) -> None:
        """
        PROBLEM 3: Permissions Consistency - FIX PERMISSIONS API
        """
        script = """
        // Override permissions.query to return consistent results
        if (navigator.permissions && navigator.permissions.query) {
            const originalQuery = navigator.permissions.query;
            navigator.permissions.query = function(descriptor) {
                return Promise.resolve({
                    state: descriptor.name === 'notifications' ? 'default' : 'granted',
                    onchange: null
                });
            };
        }
        
        // Override geolocation for consistency
        if (navigator.geolocation) {
            const originalGetCurrentPosition = navigator.geolocation.getCurrentPosition;
            navigator.geolocation.getCurrentPosition = function(success, error, options) {
                setTimeout(() => {
                    if (success) {
                        success({
                            coords: {
                                latitude: 37.7749,
                                longitude: -122.4194,
                                accuracy: 10,
                                altitude: null,
                                altitudeAccuracy: null,
                                heading: null,
                                speed: null
                            },
                            timestamp: Date.now()
                        });
                    }
                }, 100);
            };
        }
        """
        await page.add_init_script(script)

    async def apply_plugins_bypass(self, page: Page) -> None:
        """
        PROBLEM 4: Browser Plugins - ENHANCED REALISTIC PLUGINS
        """
        script = """
        // Create comprehensive plugin list
        const createMimeType = (type, description, suffixes) => ({
            type: type,
            description: description,
            suffixes: suffixes,
            enabledPlugin: null
        });
        
        const createPlugin = (name, filename, description, mimeTypes = []) => {
            const plugin = {
                name: name,
                filename: filename,
                description: description,
                length: mimeTypes.length,
                item: (index) => mimeTypes[index] || null,
                namedItem: (name) => mimeTypes.find(m => m.type === name) || null
            };
            
            // Add mimeTypes as indexed properties
            mimeTypes.forEach((mime, index) => {
                plugin[index] = mime;
                mime.enabledPlugin = plugin;
            });
            
            return plugin;
        };
        
        const plugins = [
            createPlugin(
                'Chrome PDF Plugin', 
                'internal-pdf-viewer', 
                'Portable Document Format',
                [createMimeType('application/x-google-chrome-pdf', 'Portable Document Format', 'pdf')]
            ),
            createPlugin(
                'Chrome PDF Viewer',
                'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                'Portable Document Format',
                [createMimeType('application/pdf', 'Portable Document Format', 'pdf')]
            ),
            createPlugin(
                'Native Client',
                'internal-nacl-plugin',
                'Native Client',
                [
                    createMimeType('application/x-nacl', 'Native Client Executable', ''),
                    createMimeType('application/x-pnacl', 'Portable Native Client Executable', '')
                ]
            )
        ];
        
        // Make plugins array behave like real PluginArray
        const pluginArray = Object.create(PluginArray.prototype);
        plugins.forEach((plugin, index) => {
            pluginArray[index] = plugin;
        });
        pluginArray.length = plugins.length;
        pluginArray.item = function(index) { return this[index] || null; };
        pluginArray.namedItem = function(name) { 
            return Array.from(this).find(plugin => plugin.name === name) || null; 
        };
        pluginArray.refresh = function() {};
        
        Object.defineProperty(navigator, 'plugins', {
            get: function() { return pluginArray; },
            configurable: true
        });
        
        // Also create mimeTypes array
        const allMimeTypes = plugins.flatMap(plugin => 
            Array.from({length: plugin.length}, (_, i) => plugin[i])
        );
        
        const mimeTypesArray = Object.create(MimeTypeArray.prototype);
        allMimeTypes.forEach((mime, index) => {
            mimeTypesArray[index] = mime;
        });
        mimeTypesArray.length = allMimeTypes.length;
        mimeTypesArray.item = function(index) { return this[index] || null; };
        mimeTypesArray.namedItem = function(type) { 
            return Array.from(this).find(mime => mime.type === type) || null; 
        };
        
        Object.defineProperty(navigator, 'mimeTypes', {
            get: function() { return mimeTypesArray; },
            configurable: true
        });
        """
        await page.add_init_script(script)

    async def apply_webgl_bypass(self, page: Page) -> None:
        """
        PROBLEM 5: WebGL Capabilities - ENHANCED WEBGL SPOOFING
        """
        script = """
        // Comprehensive WebGL spoofing
        const webglContexts = ['webgl', 'webgl2', 'experimental-webgl'];
        
        webglContexts.forEach(contextType => {
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type, ...args) {
                const context = originalGetContext.call(this, type, ...args);
                
                if (context && type === contextType) {
                    const originalGetParameter = context.getParameter;
                    context.getParameter = function(parameter) {
                        // Enhanced WebGL parameter spoofing
                        switch(parameter) {
                            case 37445: return 'Intel Inc.'; // VENDOR
                            case 37446: return 'Intel Iris Pro OpenGL Engine'; // RENDERER
                            case 7936: return 'WebGL 1.0 (OpenGL ES 2.0 Chromium)'; // VERSION
                            case 35724: return 'WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)'; // SHADING_LANGUAGE_VERSION
                            case 34047: return 16; // MAX_VERTEX_ATTRIBS
                            case 34076: return 16; // MAX_TEXTURE_IMAGE_UNITS
                            case 34024: return 16384; // MAX_TEXTURE_SIZE
                            case 34930: return 16384; // MAX_CUBE_MAP_TEXTURE_SIZE
                            case 3379: return 16384; // MAX_VIEWPORT_DIMS
                            case 33901: return 32; // ALIASED_POINT_SIZE_RANGE
                            case 33902: return 1; // ALIASED_LINE_WIDTH_RANGE
                            default: return originalGetParameter.call(this, parameter);
                        }
                    };
                    
                    // Spoof getExtension for consistency
                    const originalGetExtension = context.getExtension;
                    context.getExtension = function(name) {
                        // Return null for debugging extensions
                        if (name === 'WEBGL_debug_renderer_info') {
                            return null;
                        }
                        return originalGetExtension.call(this, name);
                    };
                }
                
                return context;
            };
        });
        """
        await page.add_init_script(script)

    async def apply_canvas_bypass(self, page: Page) -> None:
        """
        Canvas fingerprinting bypass with noise injection
        """
        script = """
        // Advanced Canvas fingerprinting bypass
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
        
        HTMLCanvasElement.prototype.toDataURL = function(...args) {
            const context = this.getContext('2d');
            if (context) {
                // Add minimal noise to prevent identical fingerprints
                const imageData = context.getImageData(0, 0, Math.min(1, this.width), Math.min(1, this.height));
                if (imageData.data.length > 0) {
                    // XOR with random value
                    imageData.data[0] = imageData.data[0] ^ (Math.floor(Math.random() * 3) + 1);
                    context.putImageData(imageData, 0, 0);
                }
            }
            return originalToDataURL.apply(this, args);
        };
        
        // Also patch getImageData for consistency
        CanvasRenderingContext2D.prototype.getImageData = function(...args) {
            const imageData = originalGetImageData.apply(this, args);
            // Add slight noise to prevent fingerprinting
            if (imageData.data.length > 10) {
                for (let i = 0; i < imageData.data.length; i += 100) {
                    imageData.data[i] = imageData.data[i] ^ 1;
                }
            }
            return imageData;
        };
        """
        await page.add_init_script(script)

    async def apply_timing_bypass(self, page: Page) -> None:
        """
        Prevent timing-based detection
        """
        script = """
        // Timing attack prevention
        const originalNow = performance.now;
        const originalDateNow = Date.now;
        const startTime = Date.now();
        
        performance.now = function() {
            // Add small random variance to prevent timing fingerprinting
            return originalNow.call(this) + (Math.random() - 0.5) * 0.2;
        };
        
        Date.now = function() {
            return originalDateNow() + Math.floor((Math.random() - 0.5) * 4);
        };
        
        // Also patch high resolution time
        if (window.performance && window.performance.timeOrigin) {
            Object.defineProperty(window.performance, 'timeOrigin', {
                get: () => startTime + (Math.random() - 0.5) * 10,
                configurable: true
            });
        }
        """
        await page.add_init_script(script)

    async def apply_user_agent_bypass(self, page: Page) -> None:
        """
        User Agent spoofing to remove headless indicators
        """
        script = """
        // User Agent spoofing
        const originalUserAgent = navigator.userAgent;
        const cleanUserAgent = originalUserAgent
            .replace(/HeadlessChrome/g, 'Chrome')
            .replace(/headless/gi, '');
        
        Object.defineProperty(navigator, 'userAgent', {
            get: () => cleanUserAgent,
            configurable: true
        });
        
        // Also spoof appVersion
        Object.defineProperty(navigator, 'appVersion', {
            get: () => cleanUserAgent.substring(8),
            configurable: true
        });
        
        // Spoof appName
        Object.defineProperty(navigator, 'appName', {
            get: () => 'Netscape',
            configurable: true
        });
        """
        await page.add_init_script(script)

    async def apply_platform_bypass(self, page: Page) -> None:
        """
        Platform and vendor spoofing
        """
        script = """
        // Platform information spoofing
        Object.defineProperty(navigator, 'platform', {
            get: () => 'MacIntel',
            configurable: true
        });
        
        Object.defineProperty(navigator, 'vendor', {
            get: () => 'Google Inc.',
            configurable: true
        });
        
        Object.defineProperty(navigator, 'vendorSub', {
            get: () => '',
            configurable: true
        });
        
        // Spoof hardware concurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8,
            configurable: true
        });
        
        // Spoof device memory
        if ('deviceMemory' in navigator) {
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8,
                configurable: true
            });
        }
        
        // Spoof connection
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                rtt: 50,
                downlink: 10,
                saveData: false
            }),
            configurable: true
        });
        """
        await page.add_init_script(script)

    async def apply_webdriver_removal(self, page: Page) -> None:
        """
        Enhanced webdriver removal
        """
        script = """
        // Multiple layers of webdriver removal
        
        // 1. Remove navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
            configurable: true
        });
        
        // 2. Remove from prototype
        if (navigator.webdriver !== undefined) {
            delete Object.getPrototypeOf(navigator).webdriver;
        }
        
        // 3. Remove window.webdriver
        delete window.webdriver;
        
        // 4. Override common detection methods - DISABLED to fix React compatibility
        // const originalEval = window.eval;
        // window.eval = function(str) {
        //     // This was breaking React Hot Refresh and module system
        //     return originalEval.call(this, str);
        // };
        
        // 5. Remove automation indicators
        [
            '__webdriver_evaluate', '__selenium_evaluate', '__webdriver_script_function',
            '__fxdriver_evaluate', '__driver_unwrapped', '__webdriver_unwrapped',
            '_Selenium_IDE_Recorder', '_selenium', 'calledSelenium',
            '_WEBDRIVER_ELEM_CACHE', 'ChromeDriverw', '$cdc_asdjflasutopfhvcZLmcfl_'
        ].forEach(prop => {
            delete window[prop];
            delete document[prop];
        });
        """
        await page.add_init_script(script)

    async def apply_context_stealth(self, context: BrowserContext) -> bool:
        """
        Apply stealth measures to browser context
        
        Args:
            context: Playwright browser context
            
        Returns:
            True if successful
        """
        try:
            # Basic webdriver removal at context level
            webdriver_removal_script = """
            // Context-level webdriver removal
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
                configurable: true
            });
            
            if (navigator.webdriver !== undefined) {
                delete Object.getPrototypeOf(navigator).webdriver;
            }
            """
            
            await context.add_init_script(webdriver_removal_script)
            return True
            
        except Exception as e:
            self._logger(f"❌ Context stealth failed: {e}", "error")
            return False
