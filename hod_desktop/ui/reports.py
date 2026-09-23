"""Screen 7 — Reports. Stage 1 generates sample report previews in-app."""

import tkinter as tk
from tkinter import ttk

from config.settings import Colors, Fonts
from services import reports_service
from ui.widgets import Card, SectionHeader, EmptyState


class ReportsScreen(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="App.TFrame")
        self._build()

    def _build(self):
        header = SectionHeader(self, "Reports", "Generate sample reports for your department")
        header.pack(fill="x")

        body = ttk.Frame(self, style="App.TFrame")
        body.pack(fill="both", expand=True, pady=(16, 0))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self._build_selector(body)
        self._build_preview(body)

    def _build_selector(self, parent):
        card = Card(parent)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ttk.Label(card, text="Report Type", style="H2Card.TLabel").pack(anchor="w", pady=(0, 12))

        self.type_var = tk.StringVar(value=reports_service.REPORT_TYPES[0])
        for rt in reports_service.REPORT_TYPES:
            ttk.Radiobutton(card, text=rt, value=rt, variable=self.type_var,
                            style="App.TRadiobutton").pack(anchor="w", pady=4)

        ttk.Button(card, text="Generate Report", style="Primary.TButton",
                   command=self._generate).pack(fill="x", pady=(16, 0))

        ttk.Label(
            card, text="Stage 1 note: reports are generated from live mock data "
                       "for preview only. Backend report storage/export arrives in Stage 2.",
            style="CardMuted.TLabel", wraplength=260, justify="left",
        ).pack(anchor="w", pady=(14, 0))

    def _build_preview(self, parent):
        card = Card(parent, padding=(0, 0))
        card.grid(row=0, column=1, sticky="nsew")
        card.configure(borderwidth=1, relief="solid")

        self.preview_holder = ttk.Frame(card, style="Card.TFrame")
        self.preview_holder.pack(fill="both", expand=True, padx=18, pady=18)

        self._render_empty()

    def _render_empty(self):
        for child in self.preview_holder.winfo_children():
            child.destroy()
        EmptyState(self.preview_holder, "Select a report type and click Generate.", icon="📄").pack(
            fill="both", expand=True
        )

    def _generate(self):
        report = reports_service.generate_report(self.type_var.get())

        for child in self.preview_holder.winfo_children():
            child.destroy()

        top = ttk.Frame(self.preview_holder, style="Card.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text=report["title"], style="H2Card.TLabel").pack(side="left")
        ttk.Label(top, text=f"Generated {report['generated_at']}", style="CardMuted.TLabel").pack(side="right")

        ttk.Separator(self.preview_holder, style="App.Horizontal.TSeparator").pack(fill="x", pady=10)

        text_frame = ttk.Frame(self.preview_holder, style="Card.TFrame")
        text_frame.pack(fill="both", expand=True)

        text = tk.Text(text_frame, font=("Consolas", 10), bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
                        relief="flat", wrap="word")
        vsb = ttk.Scrollbar(text_frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=vsb.set)
        text.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        text.insert("1.0", "\n".join(report["lines"]))
        text.configure(state="disabled")
