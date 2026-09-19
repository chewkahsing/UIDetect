import os
import sys
import time
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
import requests


# =========================================================
# Windows DPI Awareness
# =========================================================
# Prevent Windows from bitmap-scaling the Tkinter interface.
# This keeps text and controls sharp on high-DPI displays.
# =========================================================

if os.name == "nt":
    try:
        import ctypes

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()

    except Exception:
        pass


# =========================================================
# UIDetect Launcher Configuration
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BACKEND_DIR = os.path.join(
    BASE_DIR,
    "backend"
)


# ---------------------------------------------------------
# UIDetect runtime data directory
# ---------------------------------------------------------
# Program Files is protected from normal user write access.
# Runtime-generated files such as logs are therefore stored
# in the user's Local AppData directory.
# ---------------------------------------------------------

RUNTIME_DIR = os.path.join(
    os.environ.get(
        "LOCALAPPDATA",
        os.path.expanduser("~")
    ),
    "UIDetect"
)

os.makedirs(
    RUNTIME_DIR,
    exist_ok=True
)

BACKEND_LOG = os.path.join(
    RUNTIME_DIR,
    "backend_startup.log"
)


PYTHON_EXE = sys.executable

BACKEND_SCRIPT = os.path.join(
    BACKEND_DIR,
    "app.py"
)

OLLAMA_URL = (
    "http://127.0.0.1:11434/api/tags"
)

AI_MODEL = "qwen2.5:3b"

WINDOW_TITLE = "UIDetect"

# Modern default window size.
WINDOW_WIDTH = 850
WINDOW_HEIGHT = 750

VERSION = "1.0"

STATUS_CHECK_INTERVAL = 1000


# =========================================================
# UIDetect Launcher
# =========================================================

class UIDetectLauncher:

    def __init__(self, root):

        self.root = root

        self.root.title(
            WINDOW_TITLE
        )

        self.root.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        # -------------------------------------------------
        # Allow resizing
        # -------------------------------------------------

        self.root.resizable(
            True,
            True
        )

        # -------------------------------------------------
        # Minimum usable window size
        # -------------------------------------------------

        self.root.minsize(
            560,
            600
        )

        self.backend_process = None

        self.monitoring = True

        self.monitor_running = False

        self.closing = False

        self.setup_ui()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_launcher
        )

        self.start_backend()


    # =====================================================
    # User Interface
    # =====================================================

    def setup_ui(self):

        # =================================================
        # Main Window
        # =================================================

        self.root.configure(
            bg="#f3f5f8"
        )


        # =================================================
        # Main Container
        # =================================================

        main_frame = tk.Frame(
            self.root,
            bg="#f3f5f8"
        )

        main_frame.pack(
            fill="both",
            expand=True
        )


        # =================================================
        # Header
        # =================================================

        header_frame = tk.Frame(
            main_frame,
            bg="#172033",
            height=112
        )

        header_frame.pack(
            fill="x"
        )

        header_frame.pack_propagate(
            False
        )


        # -------------------------------------------------
        # Header content
        # -------------------------------------------------

        header_content = tk.Frame(
            header_frame,
            bg="#172033"
        )

        header_content.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=18
        )


        # Application title

        title_label = tk.Label(
            header_content,
            text="UIDetect",
            font=(
                "Segoe UI",
                24,
                "bold"
            ),
            fg="#ffffff",
            bg="#172033",
            anchor="w"
        )

        title_label.pack(
            anchor="w"
        )


        # Application subtitle

        subtitle_label = tk.Label(
            header_content,
            text=(
                "Intelligent Website Security Assessment"
            ),
            font=(
                "Segoe UI",
                10
            ),
            fg="#cbd5e1",
            bg="#172033",
            anchor="w"
        )

        subtitle_label.pack(
            anchor="w",
            pady=(2, 0)
        )


        # =================================================
        # Scrollable Area
        # =================================================

        content_container = tk.Frame(
            main_frame,
            bg="#f3f5f8"
        )

        content_container.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(18, 10)
        )


        # Canvas

        canvas = tk.Canvas(
            content_container,
            bg="#f3f5f8",
            highlightthickness=0,
            bd=0
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )


        # Right-side scrollbar

        scrollbar = tk.Scrollbar(
            content_container,
            orient="vertical",
            command=canvas.yview
        )

        scrollbar.pack(
            side="right",
            fill="y",
            padx=(8, 0)
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )


        # Scrollable frame

        scrollable_frame = tk.Frame(
            canvas,
            bg="#f3f5f8"
        )

        canvas_window = canvas.create_window(
            (0, 0),
            window=scrollable_frame,
            anchor="nw"
        )


        # =================================================
        # Scroll Region
        # =================================================

        def update_scroll_region(event=None):

            canvas.configure(
                scrollregion=canvas.bbox("all")
            )


        scrollable_frame.bind(
            "<Configure>",
            update_scroll_region
        )


        # =================================================
        # Canvas Width
        # =================================================

        def update_canvas_width(event):

            canvas.itemconfig(
                canvas_window,
                width=max(
                    event.width,
                    1
                )
            )


        canvas.bind(
            "<Configure>",
            update_canvas_width
        )


        # =================================================
        # Mouse Wheel
        # =================================================

        def mousewheel(event):

            if event.delta:

                canvas.yview_scroll(
                    int(
                        -1 *
                        (event.delta / 120)
                    ),
                    "units"
                )


        canvas.bind(
            "<Enter>",
            lambda event:
            canvas.bind_all(
                "<MouseWheel>",
                mousewheel
            )
        )

        canvas.bind(
            "<Leave>",
            lambda event:
            canvas.unbind_all(
                "<MouseWheel>"
            )
        )


        # =================================================
        # Header Information Card
        # =================================================

        intro_card = tk.Frame(
            scrollable_frame,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#e1e5eb"
        )

        intro_card.pack(
            fill="x",
            pady=(0, 14)
        )


        intro_inner = tk.Frame(
            intro_card,
            bg="#ffffff"
        )

        intro_inner.pack(
            fill="x",
            padx=20,
            pady=16
        )


        intro_title = tk.Label(
            intro_inner,
            text="Website Security Assessment",
            font=(
                "Segoe UI",
                12,
                "bold"
            ),
            fg="#172033",
            bg="#ffffff",
            anchor="w"
        )

        intro_title.pack(
            anchor="w"
        )


        intro_text = tk.Label(
            intro_inner,
            text=(
                "Use UIDetect to assess website security "
                "and receive AI-assisted recommendations "
                "before continuing with sensitive actions."
            ),
            font=(
                "Segoe UI",
                9
            ),
            fg="#5b6472",
            bg="#ffffff",
            justify="left",
            anchor="w",
            wraplength=580
        )

        intro_text.pack(
            fill="x",
            pady=(5, 0)
        )


        # =================================================
        # System Status Section
        # =================================================

        status_title = tk.Label(
            scrollable_frame,
            text="SYSTEM STATUS",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            fg="#667085",
            bg="#f3f5f8"
        )

        status_title.pack(
            anchor="w",
            pady=(0, 7)
        )


        # =================================================
        # Main System Status Card
        # =================================================

        status_card = tk.Frame(
            scrollable_frame,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#dfe4ea"
        )

        status_card.pack(
            fill="x",
            pady=(0, 16)
        )


        status_inner = tk.Frame(
            status_card,
            bg="#ffffff"
        )

        status_inner.pack(
            fill="x",
            padx=20,
            pady=18
        )


        # -------------------------------------------------
        # Main Ready Status
        # -------------------------------------------------

        self.main_status = tk.Label(
            status_inner,
            text="Starting UIDetect...",
            font=(
                "Segoe UI",
                14,
                "bold"
            ),
            fg="#c77700",
            bg="#fff8e6",
            padx=14,
            pady=12,
            anchor="center"
        )

        self.main_status.pack(
            fill="x",
            pady=(0, 16)
        )


        # -------------------------------------------------
        # Status heading
        # -------------------------------------------------

        status_details_title = tk.Label(
            status_inner,
            text="System Components",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            fg="#667085",
            bg="#ffffff",
            anchor="w"
        )

        status_details_title.pack(
            anchor="w",
            pady=(0, 7)
        )


        # -------------------------------------------------
        # Status rows
        # -------------------------------------------------

        self.backend_status = tk.Label(
            status_inner,
            text="●  Backend: Starting...",
            font=(
                "Segoe UI",
                10
            ),
            fg="#c77700",
            bg="#ffffff",
            anchor="w"
        )

        self.backend_status.pack(
            fill="x",
            pady=3
        )


        self.ollama_status = tk.Label(
            status_inner,
            text="●  Ollama: Checking...",
            font=(
                "Segoe UI",
                10
            ),
            fg="#c77700",
            bg="#ffffff",
            anchor="w"
        )

        self.ollama_status.pack(
            fill="x",
            pady=3
        )


        self.model_status = tk.Label(
            status_inner,
            text=f"●  AI Model: {AI_MODEL}",
            font=(
                "Segoe UI",
                10
            ),
            fg="#c77700",
            bg="#ffffff",
            anchor="w"
        )

        self.model_status.pack(
            fill="x",
            pady=3
        )


        # =================================================
        # Quick Actions
        # =================================================

        action_title = tk.Label(
            scrollable_frame,
            text="QUICK ACTIONS",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            fg="#667085",
            bg="#f3f5f8"
        )

        action_title.pack(
            anchor="w",
            pady=(0, 7)
        )


        action_card = tk.Frame(
            scrollable_frame,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#dfe4ea"
        )

        action_card.pack(
            fill="x",
            pady=(0, 16)
        )


        action_inner = tk.Frame(
            action_card,
            bg="#ffffff"
        )

        action_inner.pack(
            fill="x",
            padx=14,
            pady=14
        )


        # =================================================
        # Responsive Quick Action Buttons
        # =================================================

        action_buttons_frame = tk.Frame(
            action_inner,
            bg="#ffffff"
        )

        action_buttons_frame.pack(
            fill="x"
        )


        # -------------------------------------------------
        # Create simple action button
        # -------------------------------------------------

        def create_action_button(
            parent,
            title,
            command,
            state="normal"
        ):

            button = tk.Button(
                parent,
                text=title,
                font=(
                    "Segoe UI",
                    10,
                    "bold"
                ),
                bg="#f8fafc",
                fg="#172033",
                activebackground="#eef2f6",
                activeforeground="#172033",
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground="#dfe4ea",
                anchor="center",
                justify="center",
                padx=12,
                pady=12,
                cursor="hand2",
                state=state,
                command=command
            )

            return button


        # =================================================
        # Create Buttons
        # =================================================

        self.open_button = create_action_button(
            action_buttons_frame,
            "Open Chrome 🌐",
            self.open_chrome,
            state="disabled"
        )


        self.folder_button = create_action_button(
            action_buttons_frame,
            "Open Installation Folder 📁",
            self.open_installation_folder
        )


        self.manual_button = create_action_button(
            action_buttons_frame,
            "User Manual 📖",
            self.open_user_manual
        )


        self.close_button = create_action_button(
            action_buttons_frame,
            "Close ❌",
            self.close_launcher
        )


        # =================================================
        # Responsive Layout
        # =================================================
        def arrange_action_buttons(event=None):

            width = action_buttons_frame.winfo_width()

            # -------------------------------------------------
            # Remove current layout
            # -------------------------------------------------
            for button in (
                self.open_button,
                self.folder_button,
                self.manual_button,
                self.close_button
            ):
                button.grid_forget()

            # -------------------------------------------------
            # Clear previous grid configuration
            # -------------------------------------------------
            action_buttons_frame.grid_columnconfigure(
                0,
                weight=0
            )

            action_buttons_frame.grid_columnconfigure(
                1,
                weight=0
            )

            action_buttons_frame.grid_columnconfigure(
                2,
                weight=0
            )

            action_buttons_frame.grid_columnconfigure(
                3,
                weight=0
            )

            # =================================================
            # Compact / Normal Window
            #
            # Landscape-style layout
            #
            # Example:
            #
            # ┌────────────┬────────────┐
            # │ Open       │ Installation│
            # │ Chrome     │ Folder      │
            # ├────────────┼────────────┤
            # │ User       │ Close       │
            # │ Manual     │             │
            # └────────────┴────────────┘
            # =================================================
            if width < 850:

                action_buttons_frame.grid_columnconfigure(
                    0,
                    weight=1
                )

                action_buttons_frame.grid_columnconfigure(
                    1,
                    weight=1
                )

                self.open_button.grid(
                    row=0,
                    column=0,
                    sticky="ew",
                    padx=(0, 5),
                    pady=5
                )

                self.folder_button.grid(
                    row=0,
                    column=1,
                    sticky="ew",
                    padx=(5, 0),
                    pady=5
                )

                self.manual_button.grid(
                    row=1,
                    column=0,
                    sticky="ew",
                    padx=(0, 5),
                    pady=5
                )

                self.close_button.grid(
                    row=1,
                    column=1,
                    sticky="ew",
                    padx=(5, 0),
                    pady=5
                )

            # =================================================
            # Wide / Maximized Window
            #
            # Portrait-style vertical layout
            #
            # Example:
            #
            # ┌─────────────────────────────────────┐
            # │ Open Chrome                         │
            # ├─────────────────────────────────────┤
            # │ Open Installation Folder            │
            # ├─────────────────────────────────────┤
            # │ User Manual                         │
            # ├─────────────────────────────────────┤
            # │ Close                               │
            # └─────────────────────────────────────┘
            # =================================================
            else:

                action_buttons_frame.grid_columnconfigure(
                    0,
                    weight=1
                )

                self.open_button.grid(
                    row=0,
                    column=0,
                    sticky="ew",
                    pady=5
                )

                self.folder_button.grid(
                    row=1,
                    column=0,
                    sticky="ew",
                    pady=5
                )

                self.manual_button.grid(
                    row=2,
                    column=0,
                    sticky="ew",
                    pady=5
                )

                self.close_button.grid(
                    row=3,
                    column=0,
                    sticky="ew",
                    pady=5
                )

        # -------------------------------------------------
        # Re-arrange whenever the window changes size
        # -------------------------------------------------
        action_buttons_frame.bind(
            "<Configure>",
            arrange_action_buttons
        )

        # -------------------------------------------------
        # Initial layout
        # -------------------------------------------------
        action_buttons_frame.after(
            100,
            arrange_action_buttons
        )


        # =================================================
        # Load UIDetect Extension
        # =================================================

        self.load_extension_expanded = False


        self.load_extension_card = tk.Frame(
            scrollable_frame,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#dfe4ea"
        )

        self.load_extension_card.pack(
            fill="x",
            pady=(0, 10)
        )


        self.load_extension_button = tk.Button(
            self.load_extension_card,
            text="▶   1. Load UIDetect Extension",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            fg="#172033",
            bg="#ffffff",
            activebackground="#f7f9fb",
            activeforeground="#172033",
            anchor="w",
            relief="flat",
            bd=0,
            padx=16,
            pady=14,
            cursor="hand2",
            command=self.toggle_load_extension
        )

        self.load_extension_button.pack(
            fill="x"
        )


        # -------------------------------------------------
        # Extension instruction frame
        # -------------------------------------------------

        self.load_extension_frame = tk.Frame(
            self.load_extension_card,
            bg="#f8fafc"
        )


        load_inner = tk.Frame(
            self.load_extension_frame,
            bg="#f8fafc"
        )

        load_inner.pack(
            fill="x",
            padx=18,
            pady=16
        )


        load_intro = tk.Label(
            load_inner,
            text=(
                "Load UIDetect into Chrome before using "
                "the security assessment features."
            ),
            font=(
                "Segoe UI",
                9
            ),
            fg="#4b5563",
            bg="#f8fafc",
            justify="left",
            anchor="w",
            wraplength=580
        )

        load_intro.pack(
            fill="x",
            pady=(0, 12)
        )


        # -------------------------------------------------
        # Extension steps
        # -------------------------------------------------

        extension_steps = [
            (
                "1",
                "Open Chrome Extensions",
                "Go to chrome://extensions/"
            ),
            (
                "2",
                "Enable Developer mode",
                "Turn on Developer mode."
            ),
            (
                "3",
                "Load the extension",
                "Click Load unpacked."
            ),
            (
                "4",
                "Select UIDetect",
                "Choose the UIDetect folder containing manifest.json."
            ),
            (
                "5",
                "Check UIDetect",
                "Make sure UIDetect is enabled."
            ),
            (
                "6",
                "Pin UIDetect",
                "Pin the extension to the Chrome toolbar if desired."
            )
        ]


        for number, title, description in extension_steps:

            step_card = tk.Frame(
                load_inner,
                bg="#ffffff",
                highlightthickness=1,
                highlightbackground="#e3e7ed"
            )

            step_card.pack(
                fill="x",
                pady=4
            )


            step_number = tk.Label(
                step_card,
                text=number,
                font=(
                    "Segoe UI",
                    9,
                    "bold"
                ),
                fg="#ffffff",
                bg="#344054",
                width=3,
                pady=7
            )

            step_number.pack(
                side="left",
                padx=(0, 10)
            )


            step_content = tk.Frame(
                step_card,
                bg="#ffffff"
            )

            step_content.pack(
                side="left",
                fill="x",
                expand=True,
                padx=(0, 10),
                pady=7
            )


            step_title = tk.Label(
                step_content,
                text=title,
                font=(
                    "Segoe UI",
                    9,
                    "bold"
                ),
                fg="#172033",
                bg="#ffffff",
                anchor="w"
            )

            step_title.pack(
                anchor="w"
            )


            step_description = tk.Label(
                step_content,
                text=description,
                font=(
                    "Segoe UI",
                    8
                ),
                fg="#667085",
                bg="#ffffff",
                anchor="w",
                justify="left",
                wraplength=500
            )

            step_description.pack(
                anchor="w",
                pady=(1, 0)
            )


        # -------------------------------------------------
        # Extension note
        # -------------------------------------------------

        load_note = tk.Label(
            load_inner,
            text=(
                "UIDetect is loaded as an unpacked Chrome "
                "extension for development and testing."
            ),
            font=(
                "Segoe UI",
                9,
                "italic"
            ),
            fg="#667085",
            bg="#eef2f6",
            justify="left",
            anchor="w",
            wraplength=580,
            padx=12,
            pady=10
        )

        load_note.pack(
            fill="x",
            pady=(12, 0)
        )


        # =================================================
        # Start Using UIDetect
        # =================================================

        self.start_using_expanded = False


        self.start_using_card = tk.Frame(
            scrollable_frame,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#dfe4ea"
        )

        self.start_using_card.pack(
            fill="x",
            pady=(0, 10)
        )


        self.start_using_button = tk.Button(
            self.start_using_card,
            text="▶   2. Start Using UIDetect",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            fg="#172033",
            bg="#ffffff",
            activebackground="#f7f9fb",
            activeforeground="#172033",
            anchor="w",
            relief="flat",
            bd=0,
            padx=16,
            pady=14,
            cursor="hand2",
            command=self.toggle_start_using
        )

        self.start_using_button.pack(
            fill="x"
        )


        # -------------------------------------------------
        # Start Using frame
        # -------------------------------------------------

        self.start_using_frame = tk.Frame(
            self.start_using_card,
            bg="#f8fafc"
        )


        using_inner = tk.Frame(
            self.start_using_frame,
            bg="#f8fafc"
        )

        using_inner.pack(
            fill="x",
            padx=18,
            pady=16
        )


        using_intro = tk.Label(
            using_inner,
            text=(
                "Choose a UIDetect feature below to view "
                "the steps for using it."
            ),
            font=(
                "Segoe UI",
                9
            ),
            fg="#4b5563",
            bg="#f8fafc",
            justify="left",
            anchor="w",
            wraplength=580
        )

        using_intro.pack(
            fill="x",
            pady=(0, 12)
        )


        # -------------------------------------------------
        # Nested accordion helper
        # -------------------------------------------------

        def create_instruction_section(
            parent,
            title,
            steps,
            extra_text=None
        ):

            section = tk.Frame(
                parent,
                bg="#ffffff",
                highlightthickness=1,
                highlightbackground="#e1e5eb"
            )

            section.pack(
                fill="x",
                pady=4
            )


            section_state = {
                "expanded": False
            }


            section_button = tk.Button(
                section,
                text=f"▶   {title}",
                font=(
                    "Segoe UI",
                    9,
                    "bold"
                ),
                fg="#172033",
                bg="#ffffff",
                activebackground="#f7f9fb",
                activeforeground="#172033",
                anchor="w",
                relief="flat",
                bd=0,
                padx=14,
                pady=11,
                cursor="hand2"
            )

            section_button.pack(
                fill="x"
            )


            section_body = tk.Frame(
                section,
                bg="#f8fafc"
            )


            body_inner = tk.Frame(
                section_body,
                bg="#f8fafc"
            )

            body_inner.pack(
                fill="x",
                padx=16,
                pady=12
            )


            for index, step in enumerate(steps, 1):

                step_label = tk.Label(
                    body_inner,
                    text=f"{index}. {step}",
                    font=(
                        "Segoe UI",
                        9
                    ),
                    fg="#4b5563",
                    bg="#f8fafc",
                    justify="left",
                    anchor="w",
                    wraplength=540
                )

                step_label.pack(
                    fill="x",
                    pady=3
                )


            if extra_text:

                extra_label = tk.Label(
                    body_inner,
                    text=extra_text,
                    font=(
                        "Segoe UI",
                        8
                    ),
                    fg="#667085",
                    bg="#eef2f6",
                    justify="left",
                    anchor="w",
                    wraplength=540,
                    padx=10,
                    pady=8
                )

                extra_label.pack(
                    fill="x",
                    pady=(8, 0)
                )


            def toggle_section():

                if section_state["expanded"]:

                    section_body.pack_forget()

                    section_button.config(
                        text=f"▶   {title}"
                    )

                    section_state["expanded"] = False

                else:

                    section_body.pack(
                        fill="x"
                    )

                    section_button.config(
                        text=f"▼   {title}"
                    )

                    section_state["expanded"] = True


            section_button.config(
                command=toggle_section
            )


            return section


        # -------------------------------------------------
        # Dashboard Scan
        # -------------------------------------------------

        create_instruction_section(
            using_inner,
            "Dashboard Scan",
            [
                "Open a website in Google Chrome.",
                "Click the UIDetect extension.",
                "Click Scan Website.",
                "Wait for the assessment to complete.",
                "Review the security results and AI recommendation."
            ]
        )


        # -------------------------------------------------
        # Right-Click Scan
        # -------------------------------------------------

        create_instruction_section(
            using_inner,
            "Right-Click Scan",
            [
                "Right-click a website or link.",
                "Select the UIDetect scan option.",
                "Wait for the assessment to complete.",
                "Review the security results and AI recommendation."
            ]
        )


        # -------------------------------------------------
        # Interaction Action Capture
        # -------------------------------------------------

        create_instruction_section(
            using_inner,
            "Interaction Action Capture",
            [
                "Open a website in Google Chrome.",
                "Perform a detected security-sensitive action.",
                "UIDetect captures the detected action.",
                "Review the security warning and AI recommendation."
            ],
            extra_text=(
                "Detected actions may include: "
                "Login, Registration, Upload, Download, "
                "Payment, and Logout."
            )
        )


        # =================================================
        # Footer
        # =================================================

        footer_frame = tk.Frame(
            scrollable_frame,
            bg="#f3f5f8"
        )

        footer_frame.pack(
            fill="x",
            pady=(8, 14)
        )


        footer_separator = tk.Frame(
            footer_frame,
            height=1,
            bg="#dfe4ea"
        )

        footer_separator.pack(
            fill="x",
            pady=(0, 10)
        )


        version_label = tk.Label(
            footer_frame,
            text=f"UIDetect v{VERSION}",
            font=(
                "Segoe UI",
                8
            ),
            fg="#98a2b3",
            bg="#f3f5f8"
        )

        version_label.pack()


    # =====================================================
    # Status Helper
    # =====================================================

    def update_label(
        self,
        label,
        text,
        status
    ):

        status_colors = {
            "ready": "#2e7d32",
            "checking": "#c77700",
            "error": "#c62828",
            "normal": "#333333"
        }

        label.config(
            text=text,
            fg=status_colors.get(
                status,
                status_colors["normal"]
            )
        )


    # =====================================================
    # Start Backend
    # =====================================================

    def start_backend(self):

        self.update_label(
            self.backend_status,
            "●  Backend: Starting...",
            "checking"
        )

        self.update_label(
            self.ollama_status,
            "●  Ollama: Checking...",
            "checking"
        )

        self.update_label(
            self.model_status,
            "●  AI Model: Checking...",
            "checking"
        )

        self.main_status.config(
            text="Starting UIDetect backend...",
            fg="#c77700"
        )

        self.open_button.config(
            state="disabled"
        )

        thread = threading.Thread(
            target=self.launch_backend,
            daemon=True
        )

        thread.start()


    # =====================================================
    # Launch Backend
    # =====================================================

    def launch_backend(self):

        log_file = None

        try:

            # -------------------------------------------------
            # Check backend file
            # -------------------------------------------------

            if not os.path.exists(
                BACKEND_SCRIPT
            ):

                self.show_error(
                    "UIDetect backend was not found.\n\n"
                    f"Expected file:\n{BACKEND_SCRIPT}\n\n"
                    "Please reinstall UIDetect or check "
                    "the installation folder."
                )

                return


            # -------------------------------------------------
            # Check Python interpreter
            # -------------------------------------------------

            if (
                not PYTHON_EXE
                or
                not os.path.exists(PYTHON_EXE)
            ):

                self.show_error(
                    "Python was not found.\n\n"
                    "UIDetect requires Python to start "
                    "the backend.\n\n"
                    "Please reinstall UIDetect or check "
                    "the Python installation."
                )

                return


            # -------------------------------------------------
            # Prepare clean environment
            # -------------------------------------------------
            backend_env = os.environ.copy()

            backend_env.pop(
                "SSLKEYLOGFILE",
                None
            )

            # -------------------------------------------------
            # Force Python output encoding to UTF-8
            #
            # This prevents Windows "charmap" encoding errors
            # when the backend logs Unicode characters such as
            # emojis or other non-ASCII characters.
            # -------------------------------------------------
            backend_env["PYTHONIOENCODING"] = "utf-8"

            # -------------------------------------------------
            # Force Ollama host
            # -------------------------------------------------
            backend_env["OLLAMA_HOST"] = (
                "http://127.0.0.1:11434"
            )


            # -------------------------------------------------
            # Create backend log file
            # -------------------------------------------------

            log_path = BACKEND_LOG

            log_file = open(
                log_path,
                "a",
                encoding="utf-8"
            )

            log_file.write(
                "\n\n=================================================\n"
            )

            log_file.write(
                f"UIDetect backend startup: "
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            log_file.write(
                f"Python: {PYTHON_EXE}\n"
            )

            log_file.write(
                f"Backend: {BACKEND_SCRIPT}\n"
            )

            log_file.write(
                "SSLKEYLOGFILE: removed for backend process\n"
            )

            log_file.write(
                "PYTHONIOENCODING: utf-8\n"
            )

            log_file.write(
                "OLLAMA_HOST: "
                "http://127.0.0.1:11434\n"
            )

            log_file.write(
                "=================================================\n"
            )

            log_file.flush()


            # -------------------------------------------------
            # Start Flask backend
            # -------------------------------------------------

            creation_flags = 0

            if os.name == "nt":

                creation_flags = (
                    subprocess.CREATE_NO_WINDOW
                )


            self.backend_process = subprocess.Popen(
                [
                    PYTHON_EXE,
                    BACKEND_SCRIPT
                ],
                cwd=BACKEND_DIR,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                creationflags=creation_flags,
                env=backend_env
            )


            # -------------------------------------------------
            # Wait for Flask backend
            # -------------------------------------------------

            backend_ready = False

            for attempt in range(30):

                # Check process

                if (
                    self.backend_process.poll()
                    is not None
                ):

                    break


                # Test Flask server

                try:

                    response = requests.get(
                        "http://127.0.0.1:5000",
                        timeout=1
                    )

                    if response.status_code < 500:

                        backend_ready = True

                        break

                except requests.RequestException:

                    pass


                # Update startup message

                remaining = 30 - attempt

                self.root.after(
                    0,
                    lambda remaining=remaining:
                    self.main_status.config(
                        text=(
                            "Starting UIDetect backend..."
                            f" Please wait ({remaining}s)"
                        ),
                        fg="#c77700"
                    )
                )

                time.sleep(1)


            # -------------------------------------------------
            # Backend failed
            # -------------------------------------------------

            if not backend_ready:

                process_exit_code = (
                    self.backend_process.poll()
                )


                if process_exit_code is not None:

                    self.show_error(
                        "UIDetect backend failed to start.\n\n"
                        "The backend process closed unexpectedly.\n\n"
                        f"Exit code: {process_exit_code}\n\n"
                        "Please check the UIDetect backend log here:\n"
                        f"{BACKEND_LOG}"
                    )

                else:

                    self.show_error(
                        "UIDetect backend did not become ready.\n\n"
                        "The backend is still running but the Flask "
                        "server did not respond within 30 seconds.\n\n"
                        "Please check the UIDetect backend log here:\n"
                        f"{BACKEND_LOG}"
                    )

                return


            # -------------------------------------------------
            # Backend successfully started
            # -------------------------------------------------

            self.root.after(
                0,
                self.backend_ready
            )


        except Exception as error:

            self.show_error(
                "Unable to start UIDetect backend.\n\n"
                f"Error:\n{error}\n\n"
                "Please check the UIDetect backend log here:\n"
                f"{BACKEND_LOG}"
            )


        finally:

            if log_file is not None:

                try:

                    log_file.close()

                except Exception:

                    pass


    # =====================================================
    # Backend Ready
    # =====================================================

    def backend_ready(self):

        self.update_label(
            self.backend_status,
            "●  Backend: Ready",
            "ready"
        )

        self.update_label(
            self.ollama_status,
            "●  Ollama: Checking...",
            "checking"
        )

        self.update_label(
            self.model_status,
            "●  AI Model: Checking...",
            "checking"
        )

        self.main_status.config(
            text="Checking UIDetect system status...",
            fg="#c77700"
        )

        self.open_button.config(
            state="normal"
        )

        self.start_status_monitor()


    # =====================================================
    # Start Real-Time System Status Monitor
    # =====================================================

    def start_status_monitor(self):

        if self.monitor_running:

            return

        self.monitor_running = True

        thread = threading.Thread(
            target=self.monitor_system_status,
            daemon=True
        )

        thread.start()


    # =====================================================
    # Real-Time System Status Monitor
    # =====================================================

    def monitor_system_status(self):

        while self.monitoring:

            try:

                # -------------------------------------------------
                # Check Backend
                # -------------------------------------------------

                backend_running = (
                    self.backend_process is not None
                    and
                    self.backend_process.poll() is None
                )


                # -------------------------------------------------
                # Check Ollama and AI Model
                # -------------------------------------------------

                ollama_available = False

                model_available = False


                try:

                    response = requests.get(
                        OLLAMA_URL,
                        timeout=2
                    )

                    if response.status_code == 200:

                        ollama_available = True

                        data = response.json()

                        models = data.get(
                            "models",
                            []
                        )


                        for model in models:

                            model_name = model.get(
                                "name",
                                ""
                            )

                            if model_name == AI_MODEL:

                                model_available = True

                                break

                except Exception:

                    pass


                # -------------------------------------------------
                # Update User Interface
                # -------------------------------------------------

                if not self.closing:

                    try:

                        self.root.after(
                            0,
                            self.update_system_status,
                            backend_running,
                            ollama_available,
                            model_available
                        )

                    except Exception:

                        break


                # -------------------------------------------------
                # Wait
                # -------------------------------------------------

                time.sleep(
                    STATUS_CHECK_INTERVAL / 1000
                )


            except Exception:

                time.sleep(
                    STATUS_CHECK_INTERVAL / 1000
                )


        self.monitor_running = False


    # =====================================================
    # Update System Status
    # =====================================================

    def update_system_status(
        self,
        backend_running,
        ollama_available,
        model_available
    ):

        if self.closing:

            return


        # -------------------------------------------------
        # Backend Status
        # -------------------------------------------------

        if backend_running:

            self.update_label(
                self.backend_status,
                "●  Backend: Ready",
                "ready"
            )

            self.open_button.config(
                state="normal"
            )

        else:

            self.update_label(
                self.backend_status,
                "●  Backend: Stopped",
                "error"
            )

            self.open_button.config(
                state="disabled"
            )


        # -------------------------------------------------
        # Ollama Status
        # -------------------------------------------------

        if ollama_available:

            self.update_label(
                self.ollama_status,
                "●  Ollama: Available",
                "ready"
            )

        else:

            self.update_label(
                self.ollama_status,
                "●  Ollama: Not Available",
                "error"
            )


        # -------------------------------------------------
        # AI Model Status
        # -------------------------------------------------

        if not ollama_available:

            self.update_label(
                self.model_status,
                "●  AI Model: Not Available",
                "error"
            )

        elif model_available:

            self.update_label(
                self.model_status,
                f"●  AI Model: {AI_MODEL}",
                "ready"
            )

        else:

            self.update_label(
                self.model_status,
                "●  AI Model: Not Available",
                "error"
            )


        # -------------------------------------------------
        # Main Status
        # -------------------------------------------------

        if not backend_running:

            self.main_status.config(
                text=(
                    "UIDetect backend has stopped. "
                    "Please restart UIDetect."
                ),
                fg="#c62828"
            )

        elif not ollama_available:

            self.main_status.config(
                text=(
                    "Ollama is not running. "
                    "AI features are unavailable."
                ),
                fg="#c77700"
            )

        elif not model_available:

            self.main_status.config(
                text=(
                    f"AI model {AI_MODEL} is not available. "
                    "Please ensure the model is installed in Ollama."
                ),
                fg="#c77700"
            )

        else:

            self.main_status.config(
                text="UIDetect is ready to use.",
                fg="#2e7d32"
            )


    # =====================================================
    # Toggle Load UIDetect Extension
    # =====================================================

    def toggle_load_extension(self):

        if self.load_extension_expanded:

            self.load_extension_frame.pack_forget()

            self.load_extension_button.config(
                text="▶   1. Load UIDetect Extension"
            )

            self.load_extension_expanded = False

        else:

            self.load_extension_frame.pack(
                fill="x"
            )

            self.load_extension_button.config(
                text="▼   1. Load UIDetect Extension"
            )

            self.load_extension_expanded = True


    # =====================================================
    # Toggle Start Using UIDetect
    # =====================================================

    def toggle_start_using(self):

        if self.start_using_expanded:

            self.start_using_frame.pack_forget()

            self.start_using_button.config(
                text="▶   2. Start Using UIDetect"
            )

            self.start_using_expanded = False

        else:

            self.start_using_frame.pack(
                fill="x"
            )

            self.start_using_button.config(
                text="▼   2. Start Using UIDetect"
            )

            self.start_using_expanded = True


    # =====================================================
    # Open Chrome
    # =====================================================

    def open_chrome(self):

        try:

            chrome_paths = [

                os.path.expandvars(
                    r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"
                ),

                os.path.expandvars(
                    r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
                ),

                os.path.expandvars(
                    r"%LocalAppData%\Google\Chrome\Application\chrome.exe"
                )
            ]


            chrome_exe = None


            for path in chrome_paths:

                if os.path.exists(path):

                    chrome_exe = path

                    break


            if chrome_exe is None:

                messagebox.showerror(
                    "UIDetect",
                    "Google Chrome was not found on this computer."
                )

                return


            # -------------------------------------------------
            # Open Chrome normally.
            #
            # No profile is forced.
            # No Default profile is specified.
            # No chrome:// URL is opened.
            #
            # Chrome itself handles the user's current/profile
            # selection.
            # -------------------------------------------------

            subprocess.Popen(
                [
                    chrome_exe
                ],
                creationflags=subprocess.CREATE_NO_WINDOW
            )


        except Exception as error:

            messagebox.showerror(
                "UIDetect",
                f"Unable to open Chrome.\n\n{error}"
            )


    # =====================================================
    # Open Installation Folder
    # =====================================================

    def open_installation_folder(self):

        try:

            if not os.path.exists(
                BASE_DIR
            ):

                messagebox.showerror(
                    "UIDetect",
                    "The UIDetect installation folder was not found.\n\n"
                    f"Expected folder:\n{BASE_DIR}"
                )

                return


            os.startfile(
                BASE_DIR
            )


        except Exception as error:

            messagebox.showerror(
                "UIDetect",
                "Unable to open the UIDetect installation folder.\n\n"
                f"Error:\n{error}"
            )


    # =====================================================
    # Open User Manual
    # =====================================================

    def open_user_manual(self):

        try:

            github_url = (
                "https://github.com/chewkahsing/UIDetect/tree/main"
            )

            os.startfile(
                github_url
            )


        except Exception as error:

            messagebox.showerror(
                "UIDetect",
                "Unable to open the User Manual.\n\n"
                f"Error:\n{error}"
            )


    # =====================================================
    # Error
    # =====================================================

    def show_error(self, message):

        def display():

            if self.closing:

                return


            self.main_status.config(
                text="UIDetect failed to start.",
                fg="#c62828"
            )


            self.update_label(
                self.backend_status,
                "●  Backend: Failed",
                "error"
            )


            self.update_label(
                self.ollama_status,
                "●  Ollama: Not Checked",
                "normal"
            )


            self.update_label(
                self.model_status,
                "●  AI Model: Not Checked",
                "normal"
            )


            self.open_button.config(
                state="disabled"
            )


            messagebox.showerror(
                "UIDetect",
                message
            )


        self.root.after(
            0,
            display
        )


    # =====================================================
    # Close
    # =====================================================

    def close_launcher(self):

        self.closing = True

        self.monitoring = False


        if self.backend_process is not None:

            try:

                if (
                    self.backend_process.poll()
                    is None
                ):

                    self.backend_process.terminate()

            except Exception:

                pass


        self.root.destroy()


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()


    # -----------------------------------------------------
    # Set UIDetect window icon
    # -----------------------------------------------------

    icon_path = os.path.join(
        BASE_DIR,
        "UIDetect.ico"
    )


    if os.path.exists(icon_path):

        try:

            root.iconbitmap(
                icon_path
            )

        except Exception:

            pass


    app = UIDetectLauncher(
        root
    )


    root.mainloop()