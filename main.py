"""
LLM Export Tools - Desktop Application Entry Point

Global hotkey-triggered clipboard export with agentic AI format detection.

Usage:
    python main.py

Then press your configured hotkey (default: Cmd+Option+E on Mac)
"""
import sys
import signal
from src.gui.hotkey_listener import HotkeyListener
from src.gui.clipboard_manager import get_clipboard_text
from src.gui.prompt_dialog import PromptDialog
from src.gui.result_dialog import ResultDialog
from src.agent import run_export
from src.utils.logger import logger


class ExportApp:
    """
    Main application orchestrator.
    
    Manages the hotkey listener and coordinates the export workflow:
    1. User presses hotkey
    2. Get clipboard text
    3. Show prompt dialog
    4. Run LangGraph agent
    5. Show result dialog
    """
    
    def __init__(self):
        """Initialize the application."""
        self.hotkey_listener: HotkeyListener = None
        self.running = False
        
    def start(self):
        """Start the application and begin listening for hotkeys."""
        try:
            logger.info("=" * 60)
            logger.info("LLM Export Tools - Starting Desktop Application")
            logger.info("=" * 60)
            
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Create and start hotkey listener
            self.hotkey_listener = HotkeyListener(callback=self._on_hotkey_pressed)
            self.hotkey_listener.start()
            
            self.running = True
            logger.info("✓ Application started successfully")
            logger.info("✓ Hotkey listener active")
            logger.info("Press your hotkey to trigger export, or Ctrl+C to quit")
            logger.info("-" * 60)
            
            # Keep the app running
            while self.running:
                try:
                    signal.pause()  # Wait for signals
                except AttributeError:
                    # Windows doesn't have signal.pause(), use alternative
                    import time
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            logger.info("\nReceived keyboard interrupt")
            self.stop()
        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
            self.stop()
            sys.exit(1)
    
    def stop(self):
        """Stop the application and clean up resources."""
        logger.info("Shutting down application...")
        self.running = False
        
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        logger.info("✓ Application stopped")
        sys.exit(0)
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        logger.info(f"\nReceived signal {signum}")
        self.stop()
    
    def _on_hotkey_pressed(self):
        """
        Handle hotkey press event.
        
        This is the main workflow orchestrator - coordinates all components:
        1. Get clipboard text
        2. Show prompt dialog
        3. Run export agent
        4. Show result dialog
        """
        try:
            logger.info("\n" + "=" * 60)
            logger.info("🔥 HOTKEY TRIGGERED - Starting Export Workflow")
            logger.info("=" * 60)
            
            # Step 1: Get clipboard text
            logger.info("Step 1: Reading clipboard...")
            clipboard_text = get_clipboard_text()
            
            if not clipboard_text:
                logger.warning("Clipboard is empty or contains no text")
                self._show_error("Clipboard is empty", "Please copy some text first")
                return
            
            logger.info(f"✓ Retrieved {len(clipboard_text)} characters from clipboard")
            
            # Step 2: Show prompt dialog to get user instructions
            logger.info("Step 2: Showing prompt dialog...")
            dialog = PromptDialog(clipboard_text=clipboard_text)
            user_prompt = dialog.show()
            
            if not user_prompt:
                logger.info("User cancelled export")
                return
            
            logger.info(f"✓ User prompt: '{user_prompt}'")
            
            # Step 3: Run LangGraph agent
            logger.info("Step 3: Running LangGraph export agent...")
            logger.info("  → Analyzing format from prompt...")
            logger.info("  → Extracting formatting preferences...")
            logger.info("  → Routing to appropriate tool...")
            
            result = run_export(text=clipboard_text, prompt=user_prompt)
            
            logger.info(f"✓ Export complete: {result['format'].upper()} document")
            logger.info(f"✓ File: {result['file_path']}")
            
            # Step 4: Show result dialog
            logger.info("Step 4: Showing result dialog...")
            result_dialog = ResultDialog(
                file_path=result['file_path'],
                format_type=result['format']
            )
            result_dialog.show()
            
            logger.info("=" * 60)
            logger.info("✅ WORKFLOW COMPLETE - Ready for next export")
            logger.info("=" * 60 + "\n")
            
        except Exception as e:
            logger.error(f"Export workflow failed: {e}", exc_info=True)
            self._show_error("Export Failed", f"Error: {str(e)}")
    
    def _show_error(self, title: str, message: str):
        """
        Show a simple error message using tkinter.
        
        Args:
            title: Error title
            message: Error message
        """
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # Hide main window
            messagebox.showerror(title, message)
            root.destroy()
            
        except Exception as e:
            logger.error(f"Failed to show error dialog: {e}")


def main():
    """Application entry point."""
    app = ExportApp()
    app.start()


if __name__ == "__main__":
    main()

