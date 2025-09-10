#!/usr/bin/env python3
"""
SRC/PG Code Search Application

Desktop app to search SRC/PG error codes using a prebuilt trie stored in ds.pkl.gz.
Left: results (CODE | P9/P10/P11). Right: rendered HTML content via tkhtmlview.
Live search triggers when the query has at least two characters.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any, Iterable
from enum import Enum
import gzip
import pickle

try:
    from tkhtmlview import HTMLScrolledText  # type: ignore
except Exception:  # Fallback if tkhtmlview is not installed
    HTMLScrolledText = None  # Will fallback to plain Text widget

# Configuration
DEBUG = False  # Set to True to see debug logs (DEBUG, INFO, ERROR). False shows INFO and ERROR only.


class LogLevel(Enum):
    """Log levels for the application."""
    DEBUG = 0
    INFO = 1
    ERROR = 2


class FileSearchApp:
    """Main application class for the SRC/PG Code Search app."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SRC Search")
        self.root.geometry("1200x800")

        # Application state
        self.ds: Optional[Dict[str, Any]] = None
        self.current_query: str = ""
        self.results: List[Tuple[str, int, bool, str]] = []  # (code, power_gen, ispgcode, html)
        self.max_results: int = 1000
        self.truncated_more: bool = False

        # Configure dark theme
        self._configure_theme()

        # Create UI components
        self._create_widgets()

        # Configure layout
        self._configure_layout()

        # Bind events
        self._bind_events()

        # Load trie data
        self._load_ds()
        self._update_footer_info()

    def _configure_theme(self):
        """Configure the dark theme for the application."""
        # Define color scheme
        self.colors = {
            'bg_dark': '#1e1e1e',           # Main background
            'bg_light': '#1e1e1e',          # Panel backgrounds
            'fg_primary': '#e0e0e0',        # Primary text
            'fg_secondary': '#b0b0b0',      # Secondary text
            'accent': '#0d7377',            # Accent color
            'accent_hover': '#14a4aa',      # Accent hover color
            'button_bg': '#3c3c3c',         # Button background
            'button_fg': '#e0e0e0',         # Button text
            'entry_bg': '#3c3c3c',          # Entry background
            'entry_fg': '#e0e0e0',          # Entry text
            'highlight_all': '#4fc3f7',     # All matches highlight (light blue)
            'highlight_current': '#ff8a65', # Current match highlight (vivid orange)
            'scrollbar_thumb': '#505050',   # Scrollbar thumb - more visible
            'scrollbar_track': '#2a2a2a',   # Scrollbar track - darker
            'footer': '#555555'             # Footer text
        }
        
        self.root.configure(bg=self.colors['bg_dark'])
        self._configure_ttk_styles()

    def _configure_ttk_styles(self):
        """Configure TTK widget styles."""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Frame styles
        self.style.configure('Dark.TFrame', background=self.colors['bg_dark'])
        self.style.configure('Panel.TFrame', background=self.colors['bg_light'])
        # Combobox styling to match dark theme
        self.style.configure('Dark.TCombobox',
                             fieldbackground=self.colors['entry_bg'],
                             background=self.colors['entry_bg'],
                             foreground=self.colors['entry_fg'])
        try:
            self.style.map('Dark.TCombobox',
                           fieldbackground=[('readonly', self.colors['entry_bg'])],
                           foreground=[('readonly', self.colors['entry_fg'])],
                           selectbackground=[('readonly', self.colors['entry_bg'])],
                           selectforeground=[('readonly', self.colors['entry_fg'])])
        except Exception:
            pass
        
        # Label styles
        self.style.configure('Dark.TLabel', 
                           background=self.colors['bg_dark'], 
                           foreground=self.colors['fg_primary'])
        self.style.configure('Footer.TLabel',
                           background=self.colors['bg_dark'],
                           foreground=self.colors['footer'],
                           font=('Liberation Mono', 9))
        
        # Button styles
        self.style.configure('Dark.TButton',
                           background=self.colors['button_bg'],
                           foreground=self.colors['button_fg'],
                           borderwidth=1,
                           relief='flat',
                           padding=(12, 8))
        self.style.map('Dark.TButton',
                      background=[('active', self.colors['accent_hover']),
                                ('pressed', self.colors['accent'])],
                      foreground=[('active', 'white')])
        
        # PanedWindow styles
        self.style.configure('Dark.TPanedwindow', background=self.colors['bg_dark'])
        self.style.configure('Dark.TPanedwindow.Sash', 
                           background=self.colors['bg_light'],
                           sashthickness=6)

    def _create_scrollbar(self, parent, orient=tk.VERTICAL):
        """Create a styled scrollbar."""
        return tk.Scrollbar(parent,
                          orient=orient,
                          bg=self.colors['scrollbar_track'],
                          troughcolor=self.colors['scrollbar_track'],
                          activebackground=self.colors['accent'],
                          highlightbackground=self.colors['scrollbar_track'],
                          width=16,
                          relief='flat',
                          borderwidth=1,
                          elementborderwidth=1)

    def _create_text_entry(self, parent, textvariable=None):
        """Create a styled text entry."""
        return tk.Entry(parent,
                       textvariable=textvariable,
                       bg=self.colors['entry_bg'],
                       fg=self.colors['entry_fg'],
                       insertbackground=self.colors['fg_primary'],
                       relief='solid',
                       borderwidth=1,
                       font=('Liberation Mono', 11),
                       highlightthickness=1,
                       highlightcolor=self.colors['accent'])

    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Dark.TFrame')

        # Top frame for query input and power-gen filter
        self.top_frame = ttk.Frame(self.main_frame, style='Dark.TFrame')

        # Query entry with placeholder
        self.query_var = tk.StringVar()
        self.query_entry = self._create_text_entry(self.top_frame, self.query_var)
        self.query_entry.config(font=('Liberation Mono', 11))
        self._set_placeholder(self.query_entry, "Enter a SRC/PG code prefix (at least 2 characters) to search")

        # Power-gen filter combobox
        self.power_gen_var = tk.StringVar(value='ALL')
        self.power_gen_combo = ttk.Combobox(
            self.top_frame,
            textvariable=self.power_gen_var,
            values=['ALL', 'P9', 'P10', 'P11'],
            state='readonly',
            width=6,
            style='Dark.TCombobox'
        )

        # Middle frame with resizable panels
        self.middle_frame = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL, style='Dark.TPanedwindow')

        # Left panel for results list
        self.left_panel = ttk.Frame(self.middle_frame, style='Panel.TFrame')

        self.files_frame = tk.Frame(self.left_panel, bg=self.colors['bg_light'], relief='sunken', bd=1)
        self.files_listbox = tk.Listbox(
            self.files_frame,
            bg=self.colors['bg_light'],
            fg=self.colors['fg_primary'],
            selectbackground=self.colors['accent'],
            selectforeground='white',
            relief='flat',
            borderwidth=0,
            activestyle='none',
            font=('Courier', 11)
        )
        self.files_scrollbar = self._create_scrollbar(self.files_frame)

        # Right panel for HTML content
        self.right_panel = ttk.Frame(self.middle_frame, style='Panel.TFrame')
        if HTMLScrolledText is not None:
            # Use HTMLScrolledText; ensure default body styles are readable on dark theme
            self.html_view = HTMLScrolledText(self.right_panel, html='', background=self.colors['bg_light'])
        else:
            # Fallback to plain Text if tkhtmlview is not available
            self.html_view = tk.Text(self.right_panel, bg=self.colors['bg_light'], fg=self.colors['fg_primary'], wrap=tk.WORD, state=tk.DISABLED)

        # Footer
        self.footer_frame = ttk.Frame(self.main_frame, style='Dark.TFrame')
        self.footer_info_label = ttk.Label(self.footer_frame, text="", style='Footer.TLabel')
        self.footer_label = ttk.Label(self.footer_frame, text="by Mateo Velez", style='Footer.TLabel')

    def _configure_layout(self):
        """Configure the layout of all widgets."""
        # Main layout with better padding
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Top frame layout with improved spacing
        self.top_frame.pack(fill=tk.X, pady=(0, 15))
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=4)
        self.power_gen_combo.pack(side=tk.LEFT)

        # Middle frame layout - using PanedWindow with better spacing
        self.middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Add panels to PanedWindow
        self.middle_frame.add(self.left_panel)
        self.middle_frame.add(self.right_panel)

        # Left panel
        self.files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.config(yscrollcommand=self.files_scrollbar.set)
        self.files_scrollbar.config(command=self.files_listbox.yview)
        self.left_panel.configure(width=190)
        self.left_panel.pack_propagate(False)

        # Right panel - HTML view
        self.html_view.pack(fill=tk.BOTH, expand=True, padx=5)
        # Style right scrollbars to match left
        self._style_right_scrollbars()

        # Footer layout
        self.footer_frame.pack(fill=tk.X)
        self.footer_info_label.pack(side=tk.LEFT, anchor=tk.W)
        self.footer_label.pack(anchor=tk.E)

    def _bind_events(self):
        """Bind event handlers."""
        # Live query changes trigger search when >= 2 chars
        self.query_var.trace('w', self._on_query_change)

        # Power-gen selection changes trigger search
        self.power_gen_combo.bind('<<ComboboxSelected>>', lambda e: self._run_search())

        # Results list selection
        self.files_listbox.bind('<<ListboxSelect>>', self._on_result_select)

    def _log_message(self, message: str, level: LogLevel = LogLevel.INFO):
        """Print log messages to stdout based on level and DEBUG setting."""
        # Determine if we should show this log message
        should_show = False
        
        if DEBUG:
            # Show all levels when DEBUG is True
            should_show = True
        else:
            # Show only INFO and ERROR when DEBUG is False
            should_show = level in (LogLevel.INFO, LogLevel.ERROR)
        
        if should_show:
            # Add level prefix for clarity
            level_prefix = {
                LogLevel.DEBUG: "[DEBUG]",
                LogLevel.INFO: "[INFO]",
                LogLevel.ERROR: "[ERROR]"
            }
            
            formatted_message = f"{level_prefix[level]} {message}"
            print(formatted_message)

    def _on_query_change(self, *args):
        """Handle query text change (live search)."""
        # Trigger search only when at least 2 characters (excluding placeholder)
        text = self.query_var.get().strip()
        if not text or text == getattr(self.query_entry, 'placeholder', ''):
            self._clear_results()
            self._clear_html()
            return
        if len(text) < 2:
            self._clear_results()
            self._clear_html()
            return
        self.current_query = text
        self._run_search()

    def _run_search(self):
        """Run the trie-based search with power-gen filter and populate results (limit 1000)."""
        if self.ds is None:
            return

        query = self._normalize_query(self.current_query)
        if not query:
            self._clear_results()
            self._clear_html()
            return

        decomposed = list(query)
        selected_pgen = self.power_gen_var.get()

        new_results: List[Tuple[str, int, bool, str]] = []
        self.truncated_more = False
        try:
            for value in self._iter_search(self.ds, decomposed):
                # value is a tuple: (title, power_gen, ispgcode, article_clean_html)
                try:
                    code: str = value[0]
                    power_gen: int = int(value[1]) if value[1] is not None else 0
                    is_pg: bool = bool(value[2])
                    html: str = value[3]
                except Exception:
                    continue

                if selected_pgen != 'ALL' and f"P{power_gen}" != selected_pgen:
                    continue

                new_results.append((code, power_gen, is_pg, html))
                if len(new_results) >= self.max_results:
                    self.truncated_more = True
                    break
        except Exception as e:
            self._log_message(f"Search error: {str(e)}", LogLevel.ERROR)
            new_results = []

        # Update UI
        self.results = new_results
        self.files_listbox.delete(0, tk.END)
        for code, power_gen, is_pg, _ in self.results:
            display = self._format_list_row(code, power_gen, is_pg)
            self.files_listbox.insert(tk.END, display)

        self._update_footer_info()

    def _on_result_select(self, event):
        """Handle result selection to render HTML content on the right panel."""
        selection = self.files_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index < 0 or index >= len(self.results):
            return
        _, _, _, html = self.results[index]
        self._render_html(html)

    def _render_html(self, html: str):
        """Render HTML in the right panel using tkhtmlview (fallback to plain text if unavailable)."""
        if HTMLScrolledText is not None and isinstance(self.html_view, HTMLScrolledText):
            try:
                # Keep it simple and avoid CSS leaking: just wrap content
                wrapped = f"<div style=\"color:{self.colors['fg_primary']}\">{html or ''}</div>"
                self.html_view.set_html(wrapped)
            except Exception as e:
                self._log_message(f"HTML render error: {str(e)}", LogLevel.ERROR)
                self.html_view.set_html("<p>Error rendering HTML content.</p>")
        else:
            # Fallback plain text
            self.html_view.config(state=tk.NORMAL)
            self.html_view.delete(1.0, tk.END)
            self.html_view.insert(1.0, html or "")
            self.html_view.config(state=tk.DISABLED)

    def _clear_results(self):
        self.results = []
        self.files_listbox.delete(0, tk.END)
        self._update_footer_info()

    def _clear_html(self):
        if HTMLScrolledText is not None and isinstance(self.html_view, HTMLScrolledText):
            try:
                self.html_view.set_html("")
            except Exception:
                pass
        else:
            self.html_view.config(state=tk.NORMAL)
            self.html_view.delete(1.0, tk.END)
            self.html_view.config(state=tk.DISABLED)

    def _normalize_query(self, q: str) -> str:
        q = (q or "").strip().upper()
        # Support X/Y as wildcard placeholders like the dataset uses
        q = q.replace('X', '*').replace('Y', '*')
        return q

    def _format_list_row(self, code: str, power_gen: int, is_pg: bool) -> str:
        selected = self.power_gen_var.get() if hasattr(self, 'power_gen_var') else 'ALL'
        pgen = f"P{power_gen}" if power_gen in (9, 10, 11) else "P?"
        if selected == 'ALL':
            return f"{code} | {pgen}"
        return f"{code}"
    
    def _update_footer_info(self):
        """Update the footer info display with result count and inferred type."""
        total = len(self.results)
        if total > 0:
            code_type = self._infer_code_type()
            plural = 'PGs' if code_type == 'PG' else 'SRCs'
            count_display = f"{self.max_results}+" if (self.truncated_more and total >= self.max_results) else str(total)
            info_text = f"Found {count_display} {plural}"
            self.footer_info_label.config(text=info_text)
        else:
            self.footer_info_label.config(text="")

    def _infer_code_type(self) -> str:
        """Infer code type (PG or SRC) from the first two characters; fallback to first result."""
        prefix = (self.current_query or "").strip().upper()[:2]
        # get first result and return type
        if self.results:
            return 'PG' if self.results[0][2] else 'SRC'
        return 'SRC'
    
    def _set_placeholder(self, entry_widget, placeholder_text):
        """Set placeholder text for an entry widget."""
        entry_widget.placeholder = placeholder_text
        entry_widget.placeholder_color = self.colors['fg_secondary']
        entry_widget.default_color = self.colors['entry_fg']
        
        def on_focus_in(event):
            if entry_widget.get() == placeholder_text:
                entry_widget.delete(0, tk.END)
                entry_widget.config(fg=entry_widget.default_color)
        
        def on_focus_out(event):
            if not entry_widget.get():
                entry_widget.insert(0, placeholder_text)
                entry_widget.config(fg=entry_widget.placeholder_color)
        
        # Set initial placeholder
        entry_widget.insert(0, placeholder_text)
        entry_widget.config(fg=entry_widget.placeholder_color)
        
        # Bind events
        entry_widget.bind('<FocusIn>', on_focus_in)
        entry_widget.bind('<FocusOut>', on_focus_out)
    
    def _load_ds(self):
        """Load trie data from ds.pkl.gz at startup."""
        try:
            ds_path = Path(__file__).parent / 'data.pkl.gz'
            if not ds_path.exists():
                message = f"Data file not found: {ds_path}"
                self._log_message(message, LogLevel.ERROR)
                messagebox.showerror("Data Missing", message)
                return
            with gzip.open(ds_path, 'rb') as f:
                self.ds = pickle.load(f)
            self._log_message("Trie data loaded successfully", LogLevel.INFO)
        except Exception as e:
            self._log_message(f"Failed to load trie data: {str(e)}", LogLevel.ERROR)
            messagebox.showerror("Load Error", f"Failed to load data: {str(e)}")

    # ===== Trie search helpers (based on final.ipynb) =====
    def _iter_all(self, ds: Dict[str, Any]) -> Iterable[Tuple[Any, ...]]:
        yield from ds.get('', [])
        if '*' in ds:
            yield from self._iter_all(ds['*'])
        for key in ds:
            if key != '' and key != '*':
                yield from self._iter_all(ds[key])

    def _iter_search(self, ds: Dict[str, Any], decomposed_key: List[str]) -> Iterable[Tuple[Any, ...]]:
        if decomposed_key:
            head = decomposed_key[0]
            tail = decomposed_key[1:]
            if head in ds:
                yield from self._iter_search(ds[head], tail)
            
            # Add wildcard search
            if '*' in ds:
                yield from self._iter_search(ds['*'], tail)
        else:
            yield from self._iter_all(ds)

    # ===== UI helpers =====
    def _style_right_scrollbars(self):
        """Style scrollbars in the right panel (including tkhtmlview internals)."""
        try:
            def walk(widget):
                # Style native tk.Scrollbar widgets
                if isinstance(widget, tk.Scrollbar):
                    widget.config(
                        bg=self.colors['scrollbar_track'],
                        troughcolor=self.colors['scrollbar_track'],
                        activebackground=self.colors['accent'],
                        highlightbackground=self.colors['scrollbar_track'],
                        width=16,
                        relief='flat',
                        borderwidth=1,
                        elementborderwidth=1,
                    )
                for child in widget.winfo_children():
                    walk(child)
            walk(self.right_panel)
        except Exception:
            pass


def main():
    """Main entry point for the application."""
    # To enable debug logging, change DEBUG = True at the top of this file
    root = tk.Tk()
    app = FileSearchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()