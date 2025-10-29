"""
Prompt dialog for getting user's export preferences.

Uses tkinter to show a clean dialog where users specify format and formatting.
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional
from src.utils.logger import logger


class PromptDialog:
    """
    Dialog to get export preferences from user.
    
    Shows clipboard preview and asks for export instructions.
    
    Example:
        dialog = PromptDialog(clipboard_text="Sample content...")
        prompt = dialog.show()
        
        if prompt:
            print(f"User wants: {prompt}")
        else:
            print("User cancelled")
    """
    
    def __init__(self, clipboard_text: str):
        """
        Initialize the prompt dialog.
        
        Args:
            clipboard_text: Text from clipboard (for preview)
        """
        self.clipboard_text = clipboard_text
        self.result: Optional[str] = None
        self.root: Optional[tk.Tk] = None
    
    def show(self) -> Optional[str]:
        """
        Show the dialog and wait for user input.
        
        Returns:
            str: User's prompt/instructions, or None if cancelled
        """
        try:
            # Create root window
            self.root = tk.Tk()
            self.root.title("LLM Export Tools")
            self.root.geometry("500x350")
            self.root.resizable(True, True)
            
            # Center window on screen
            self._center_window()
            
            # Build UI
            self._build_ui()
            
            # Make dialog modal
            self.root.grab_set()
            self.root.focus_force()
            
            # Wait for user to close dialog
            self.root.mainloop()
            
            logger.debug(f"Prompt dialog result: {self.result}")
            return self.result
            
        except Exception as e:
            logger.error(f"Failed to show prompt dialog: {e}")
            return None
    
    def _center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _build_ui(self):
        """Build the dialog UI components."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Export Clipboard Text",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Clipboard preview section
        preview_label = ttk.Label(
            main_frame,
            text="Clipboard Preview:",
            font=("Arial", 10, "bold")
        )
        preview_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Preview text (scrollable)
        preview_frame = ttk.Frame(main_frame)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        preview_text = tk.Text(
            preview_frame,
            height=6,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="#f5f5f5",
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(preview_frame, command=preview_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        preview_text.config(yscrollcommand=scrollbar.set)
        
        # Insert preview text
        preview_text.config(state=tk.NORMAL)
        preview = self.clipboard_text[:500] + ("..." if len(self.clipboard_text) > 500 else "")
        preview_text.insert("1.0", preview)
        preview_text.config(state=tk.DISABLED)
        
        # Prompt input section
        prompt_label = ttk.Label(
            main_frame,
            text="Export Instructions:",
            font=("Arial", 10, "bold")
        )
        prompt_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Prompt entry
        self.prompt_entry = ttk.Entry(
            main_frame,
            font=("Arial", 11)
        )
        self.prompt_entry.pack(fill=tk.X, pady=(0, 5))
        self.prompt_entry.focus()
        
        # Placeholder examples
        examples_label = ttk.Label(
            main_frame,
            text='e.g., "Export as Word with Arial 14pt, bold" or "Save as PDF with 1-inch margins"',
            font=("Arial", 9),
            foreground="gray"
        )
        examples_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Bind Enter key to OK
        self.prompt_entry.bind("<Return>", lambda e: self._on_ok())
        self.prompt_entry.bind("<Escape>", lambda e: self._on_cancel())
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Cancel button
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # OK button
        ok_btn = ttk.Button(
            button_frame,
            text="Export",
            command=self._on_ok
        )
        ok_btn.pack(side=tk.RIGHT)
    
    def _on_ok(self):
        """Handle OK button click."""
        prompt = self.prompt_entry.get().strip()
        
        if not prompt:
            logger.warning("Empty prompt provided")
            # Show a simple message
            error_label = ttk.Label(
                self.root,
                text="Please enter export instructions",
                foreground="red",
                font=("Arial", 9)
            )
            error_label.place(relx=0.5, rely=0.92, anchor=tk.CENTER)
            return
        
        self.result = prompt
        self.root.quit()
        self.root.destroy()
    
    def _on_cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.root.quit()
        self.root.destroy()

