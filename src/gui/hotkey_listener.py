"""
Global hotkey listener using pynput.

Listens for configured hotkey combination and triggers export workflow.
"""
from typing import Callable, Optional
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
from config.settings import get_hotkey
from src.utils.logger import logger


class HotkeyListener:
    """
    Global hotkey listener for triggering exports.
    
    Listens for a configured hotkey combination (e.g., Cmd+Option+E on Mac)
    and executes a callback when pressed.
    
    Example:
        def on_hotkey_pressed():
            print("Hotkey triggered!")
        
        listener = HotkeyListener(callback=on_hotkey_pressed)
        listener.start()
        # ... app runs ...
        listener.stop()
    """
    
    def __init__(self, callback: Callable[[], None]):
        """
        Initialize the hotkey listener.
        
        Args:
            callback: Function to call when hotkey is pressed
        """
        self.callback = callback
        self.listener: Optional[keyboard.Listener] = None
        self.hotkey_combo = self._parse_hotkey()
        
        logger.info(f"Hotkey listener initialized with combination: {self.hotkey_combo}")
    
    def _parse_hotkey(self) -> keyboard.HotKey:
        """
        Parse hotkey string from settings into pynput format.
        
        Returns:
            keyboard.HotKey: Parsed hotkey combination
        """
        hotkey_str = get_hotkey()
        
        # Parse the hotkey string (e.g., "<cmd>+<option>+e")
        # pynput uses a different format, so we need to convert
        try:
            # Create a HotKey with the parsed combination
            hotkey = keyboard.HotKey(
                keyboard.HotKey.parse(hotkey_str),
                self.callback
            )
            logger.debug(f"Parsed hotkey: {hotkey_str}")
            return hotkey
            
        except Exception as e:
            logger.error(f"Failed to parse hotkey '{hotkey_str}': {e}")
            # Fallback to a default
            fallback = "<cmd>+<option>+e"
            logger.warning(f"Using fallback hotkey: {fallback}")
            return keyboard.HotKey(
                keyboard.HotKey.parse(fallback),
                self.callback
            )
    
    def start(self):
        """
        Start listening for the hotkey in a background thread.
        
        This is non-blocking and runs until stop() is called.
        """
        if self.listener is not None:
            logger.warning("Hotkey listener already running")
            return
        
        try:
            # Create listener with key press/release handlers
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            
            self.listener.start()
            logger.info("Hotkey listener started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {e}")
            raise
    
    def stop(self):
        """
        Stop the hotkey listener.
        """
        if self.listener is None:
            logger.warning("Hotkey listener not running")
            return
        
        try:
            self.listener.stop()
            self.listener = None
            logger.info("Hotkey listener stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop hotkey listener: {e}")
    
    def _on_press(self, key):
        """
        Handle key press events.
        
        Args:
            key: The key that was pressed
        """
        try:
            self.hotkey_combo.press(key)
        except Exception as e:
            logger.debug(f"Key press error: {e}")
    
    def _on_release(self, key):
        """
        Handle key release events.
        
        Args:
            key: The key that was released
        """
        try:
            self.hotkey_combo.release(key)
        except Exception as e:
            logger.debug(f"Key release error: {e}")
    
    def is_running(self) -> bool:
        """
        Check if the listener is currently running.
        
        Returns:
            bool: True if running, False otherwise
        """
        return self.listener is not None and self.listener.is_alive()

