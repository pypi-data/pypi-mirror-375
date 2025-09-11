"""
Script Manager - JavaScript execution and evaluation manager
Layer 2.5: JavaScript Integration - Handles script execution, API calls, and result processing
"""

import asyncio
import json
from typing import Any, Dict, Optional, Union, List
from datetime import datetime, timezone
from playwright.async_api import Page

from .logger_bridge import BrowserLoggerBridge as LoggingBridge


class ScriptManager:
    """Manager for JavaScript execution and evaluation"""
    
    def __init__(self, page: Optional[Page], logger_bridge: LoggingBridge):
        self._page = page
        self.logger_bridge = logger_bridge
        self.allow_logging = False

        # Statistics
        self._scripts_executed = 0
        self._scripts_successful = 0
        self._scripts_failed = 0
        self._api_calls_made = 0
        self._execution_history: List[Dict[str, Any]] = []
    
    def update_page(self, page: Optional[Page]):
        """Update the page reference"""
        self._page = page

    def log_error(self, message: str):
        """Log error"""
        if not self.allow_logging:
            return
        self.logger_bridge.log_error(message)

    def log_info(self, message: str):
        """Log info"""
        if not self.allow_logging:
            return
        self.logger_bridge.log_info(message)
        
    def log_debug(self, message: str):
        """Log debug"""
        if not self.allow_logging:
            return
        self.logger_bridge.log_debug(message)
        
    async def execute_script(self, script: str, timeout: int = 30000) -> Any:
        """
        Execute JavaScript code and return result
        
        Args:
            script: JavaScript code to execute
            timeout: Timeout in milliseconds
            
        Returns:
            Script execution result
        """
        if not self._page:
            raise RuntimeError("No page available for script execution")
        
        start_time = datetime.now()
        self._scripts_executed += 1
        
        try:
            self.log_info(f"🔧 Executing JavaScript (timeout: {timeout}ms)")
            self.log_debug(f"Script preview: {script[:100]}...")
            
            # Execute script with timeout
            result = await asyncio.wait_for(
                self._page.evaluate(script),
                timeout=timeout / 1000
            )
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._scripts_successful += 1
            
            # Log execution details
            execution_record = {
                "timestamp": start_time.isoformat(),
                "duration_ms": duration_ms,
                "success": True,
                "result_type": type(result).__name__,
                "script_length": len(script),
            }
            self._execution_history.append(execution_record)
            
            self.log_info(f"✅ Script executed successfully ({duration_ms:.1f}ms)")
            self.log_debug(f"Result type: {type(result).__name__}")
            
            return result
            
        except asyncio.TimeoutError:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._scripts_failed += 1
            
            execution_record = {
                "timestamp": start_time.isoformat(),
                "duration_ms": duration_ms,
                "success": False,
                "error": "Timeout",
                "script_length": len(script),
            }
            self._execution_history.append(execution_record)
            
            self.log_error(f"⏰ Script execution timeout ({timeout}ms)")
            raise
            
        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._scripts_failed += 1
            
            execution_record = {
                "timestamp": start_time.isoformat(),
                "duration_ms": duration_ms,
                "success": False,
                "error": str(e),
                "script_length": len(script),
            }
            self._execution_history.append(execution_record)
            
            self.log_error(f"❌ Script execution failed: {e}")
            raise
    
    async def execute_api_call(self, api_url: str, headers: Dict[str, str], method: str = "GET", timeout: int = 30000) -> Dict[str, Any]:
        """
        Execute API call via JavaScript fetch
        
        Args:
            api_url: API endpoint URL
            headers: HTTP headers
            method: HTTP method
            timeout: Timeout in milliseconds
            
        Returns:
            API response data
        """
        self._api_calls_made += 1
        
        # Build fetch script
        headers_json = json.dumps(headers)
        
        script = f"""
        (async function() {{
            try {{
                const response = await fetch('{api_url}', {{
                    method: '{method}',
                    headers: {headers_json}
                }});
                
                if (!response.ok) {{
                    throw new Error('HTTP error! status: ' + response.status);
                }}
                
                const data = await response.json();
                return data;
            }} catch (error) {{
                return {{ error: error.message }};
            }}
        }})()
        """
        
        self.log_info(f"🌐 Making API call: {method} {api_url}")
        
        result = await self.execute_script(script, timeout)
        
        if isinstance(result, dict) and 'error' in result:
            self.log_error(f"❌ API call failed: {result['error']}")
        else:
            self.log_info(f"✅ API call successful")
        
        return result
    
    
    async def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """
        Wait for element using JavaScript
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
            
        Returns:
            True if element found
        """
        script = f"""
        (function() {{
            return new Promise((resolve) => {{
                const element = document.querySelector('{selector}');
                if (element) {{
                    resolve(true);
                    return;
                }}
                
                const observer = new MutationObserver(() => {{
                    const element = document.querySelector('{selector}');
                    if (element) {{
                        observer.disconnect();
                        resolve(true);
                    }}
                }});
                
                observer.observe(document.body, {{
                    childList: true,
                    subtree: true
                }});
                
                setTimeout(() => {{
                    observer.disconnect();
                    resolve(false);
                }}, {timeout});
            }});
        }})()
        """
        
        self.log_info(f"🎯 Waiting for element: {selector}")
        
        try:
            result = await self.execute_script(script, timeout + 1000)
            if result:
                self.log_info(f"✅ Element found: {selector}")
            else:
                self.log_warning(f"⏰ Element timeout: {selector}")
            return result
        except Exception as e:
            self.log_error(f"❌ Element wait failed: {selector} - {e}")
            return False
    
    async def inject_helper_functions(self) -> bool:
        """
        Inject helper JavaScript functions into page
        
        Returns:
            True if injection successful
        """
        helper_script = """
        window.unrealonHelpers = {
            // Wait for element with promise
            waitForElement: function(selector, timeout = 10000) {
                return new Promise((resolve) => {
                    const element = document.querySelector(selector);
                    if (element) {
                        resolve(element);
                        return;
                    }
                    
                    const observer = new MutationObserver(() => {
                        const element = document.querySelector(selector);
                        if (element) {
                            observer.disconnect();
                            resolve(element);
                        }
                    });
                    
                    observer.observe(document.body, {
                        childList: true,
                        subtree: true
                    });
                    
                    setTimeout(() => {
                        observer.disconnect();
                        resolve(null);
                    }, timeout);
                });
            },
            
            // Get page info
            getPageInfo: function() {
                return {
                    url: window.location.href,
                    title: document.title,
                    readyState: document.readyState,
                    timestamp: new Date().toISOString()
                };
            },
            
            // Check if SPA loaded
            isSPAReady: function() {
                return document.readyState === 'complete' && 
                       document.querySelector('body').children.length > 0;
            }
        };
        
        console.log('🔧 UnrealOn helper functions injected');
        """
        
        try:
            await self.execute_script(helper_script)
            self.log_info("🔧 Helper functions injected successfully")
            return True
        except Exception as e:
            self.log_error(f"❌ Failed to inject helper functions: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get script execution statistics"""
        success_rate = (self._scripts_successful / self._scripts_executed * 100) if self._scripts_executed > 0 else 0
        
        return {
            "scripts_executed": self._scripts_executed,
            "scripts_successful": self._scripts_successful,
            "scripts_failed": self._scripts_failed,
            "success_rate": success_rate,
            "api_calls_made": self._api_calls_made,
            "execution_history_count": len(self._execution_history),
        }
    
    def print_statistics(self) -> None:
        """Print script execution statistics"""
        stats = self.get_statistics()
        
        print("\n🔧 Script Manager Statistics:")
        print(f"   Scripts executed: {stats['scripts_executed']}")
        print(f"   Successful: {stats['scripts_successful']}")
        print(f"   Failed: {stats['scripts_failed']}")
        print(f"   Success rate: {stats['success_rate']:.1f}%")
        print(f"   API calls made: {stats['api_calls_made']}")
        
        # Show recent executions
        if self._execution_history:
            print("   Recent executions:")
            for execution in self._execution_history[-3:]:  # Show last 3
                status = "✅" if execution["success"] else "❌"
                print(f"     {status} {execution['duration_ms']:.1f}ms")
    
    def clear_history(self) -> None:
        """Clear execution history"""
        self._execution_history.clear()
        self.log_info("🧹 Cleared script execution history")
