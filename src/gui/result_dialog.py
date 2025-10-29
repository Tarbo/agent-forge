"""
Result dialog showing export success with file actions.

Shows the exported file path with options to open or close.
"""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from src.utils.file_manager import open_file
from src.utils.logger import logger


class ResultDialog:
    """
    Dialog showing export result with action buttons.
    
    Displays success message, file path, and buttons to open or close.
    
    Example:
        dialog = ResultDialog(
            file_path="/Users/me/exports/document_2024-10-29.docx",
            format_type="word"
        )
        dialog.show()
    """
    
    def __init__(self, file_path: str, format_type: str):
        """
        Initialize the result dialog.
        
        Args:
            file_path: Full path to the exported file
            format_type: Export format (word, pdf, etc.)
        """
        self.file_path = Path(file_path)
        self.format_type = format_type.upper()
        self.root: tk.Tk = None
    
    def show(self):
        """
        Show the result dialog.
        
        Non-blocking - dialog stays open until user clicks a button.
        """
        try:
            # Create root window
            self.root = tk.Tk()
            self.root.title("Export Complete")
            self.root.geometry("550x250")
            self.root.resizable(True, True)
            
            # Center window on screen
            self._center_window()
            
            # Build UI
            self._build_ui()
            
            # Make dialog modal
            self.root.grab_set()
            self.root.focus_force()
            
            # Run dialog
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Failed to show result dialog: {e}")
    
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
        
        # Success icon and title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(pady=(0, 20))
        
        # Success emoji/icon
        icon_label = ttk.Label(
            title_frame,
            text="✅",
            font=("Arial", 32)
        )
        icon_label.pack()
        
        # Success message
        success_label = ttk.Label(
            title_frame,
            text=f"{self.format_type} Document Exported Successfully!",
            font=("Arial", 14, "bold")
        )
        success_label.pack(pady=(10, 0))
        
        # File path section
        path_frame = ttk.LabelFrame(main_frame, text="File Location", padding="10")
        path_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # File path (read-only, selectable)
        path_text = tk.Text(
            path_frame,
            height=3,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="#f5f5f5",
            relief=tk.FLAT,
            state=tk.NORMAL
        )
        path_text.pack(fill=tk.BOTH, expand=True)
        
        # Insert file path
        path_text.insert("1.0", str(self.file_path))
        path_text.config(state=tk.DISABLED)
        
        # File info
        file_size = self.file_path.stat().st_size if self.file_path.exists() else 0
        size_kb = file_size / 1024
        
        info_label = ttk.Label(
            path_frame,
            text=f"Size: {size_kb:.1f} KB",
            font=("Arial", 9),
            foreground="gray"
        )
        info_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Done button
        done_btn = ttk.Button(
            button_frame,
            text="Done",
            command=self._on_done
        )
        done_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Open File button
        open_btn = ttk.Button(
            button_frame,
            text="Open File",
            command=self._on_open_file
        )
        open_btn.pack(side=tk.RIGHT)
        
        # Copy Path button
        copy_btn = ttk.Button(
            button_frame,
            text="Copy Path",
            command=self._on_copy_path
        )
        copy_btn.pack(side=tk.LEFT)
        
        # Keyboard shortcuts
        self.root.bind("<Return>", lambda e: self._on_open_file())
        self.root.bind("<Escape>", lambda e: self._on_done())
    
    def _on_open_file(self):
        """Handle Open File button click."""
        try:
            if open_file(self.file_path):
                logger.info(f"Opened file: {self.file_path}")
            else:
                logger.warning(f"Failed to open file: {self.file_path}")
                # Show error message
                error_label = ttk.Label(
                    self.root,
                    text="Failed to open file. Please open manually.",
                    foreground="red",
                    font=("Arial", 9)
                )
                error_label.place(relx=0.5, rely=0.92, anchor=tk.CENTER)
        except Exception as e:
            logger.error(f"Error opening file: {e}")
    
    def _on_copy_path(self):
        """Handle Copy Path button click."""
        try:
            import pyperclip
            pyperclip.copy(str(self.file_path))
            logger.info("File path copied to clipboard")
            
            # Show confirmation
            confirm_label = ttk.Label(
                self.root,
                text="✓ Path copied to clipboard",
                foreground="green",
                font=("Arial", 9)
            )
            confirm_label.place(relx=0.5, rely=0.92, anchor=tk.CENTER)
            
            # Remove after 2 seconds
            self.root.after(2000, confirm_label.destroy)
            
        except Exception as e:
            logger.error(f"Failed to copy path: {e}")
    
    def _on_done(self):
        """Handle Done button click."""
        self.root.quit()
        self.root.destroy()

