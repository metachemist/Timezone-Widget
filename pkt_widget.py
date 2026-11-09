#!/usr/bin/env python3
"""
PKT Time Zone Converter Widget
================================
A lightweight, frameless desktop widget that displays live Pakistan Standard
Time (PKT, Asia/Karachi, UTC+5) and converts any global IANA time zone to PKT.

Requirements:
    pip install customtkinter          # for best visuals (optional)
    pip install tzdata                 # required on Windows; optional on Linux/macOS

Python >= 3.9 (uses zoneinfo from stdlib)
"""

import sys
import re
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, available_timezones

# ─── Constants ────────────────────────────────────────────────────────────────

PKT = ZoneInfo("Asia/Karachi")
PKT_LABEL = "Pakistan Standard Time (PKT · UTC+5)"

# Dark-mode colour palette
BG_DARK        = "#1a1a2e"   # deep navy background
BG_CARD        = "#16213e"   # slightly lighter card/panel
BG_INPUT       = "#0f3460"   # input field background
ACCENT         = "#e94560"   # red accent
ACCENT2        = "#533483"   # purple accent
TEXT_PRIMARY   = "#eaeaea"   # near-white
TEXT_SECONDARY = "#a0a0b0"   # muted
TEXT_MUTED     = "#606070"   # very muted
GREEN          = "#00d4aa"   # positive/success
ORANGE         = "#ffb347"   # warning/offset
BORDER         = "#2a2a4a"   # subtle border

# Fonts – fall back gracefully if the preferred face is missing
FONT_FACE  = "Segoe UI" if sys.platform == "win32" else "SF Pro Display" if sys.platform == "darwin" else "Ubuntu"
FONT_MONO  = "Consolas" if sys.platform == "win32" else "Menlo" if sys.platform == "darwin" else "Ubuntu Mono"

W, H = 360, 300   # widget dimensions in pixels

# ─── Helpers ──────────────────────────────────────────────────────────────────

def sorted_timezones() -> list[str]:
    """Return all IANA time zones sorted, with common ones promoted to top."""
    popular = [
        "America/New_York", "America/Chicago", "America/Denver",
        "America/Los_Angeles", "America/Toronto", "America/Vancouver",
        "America/Sao_Paulo", "America/Mexico_City", "America/Bogota",
        "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Rome",
        "Europe/Istanbul", "Europe/Moscow", "Europe/Amsterdam",
        "Asia/Karachi", "Asia/Dubai", "Asia/Kolkata", "Asia/Dhaka",
        "Asia/Kabul", "Asia/Tashkent", "Asia/Almaty",
        "Asia/Tokyo", "Asia/Shanghai", "Asia/Hong_Kong", "Asia/Singapore",
        "Asia/Seoul", "Asia/Bangkok", "Asia/Jakarta",
        "Asia/Tehran", "Asia/Baghdad", "Asia/Riyadh", "Asia/Beirut",
        "Africa/Cairo", "Africa/Nairobi", "Africa/Lagos",
        "Australia/Sydney", "Australia/Melbourne", "Pacific/Auckland",
        "Pacific/Honolulu", "UTC",
    ]
    all_tz = sorted(available_timezones())
    # popular first (deduplicated), then the rest
    seen = set()
    result = []
    for tz in popular:
        if tz in all_tz and tz not in seen:
            result.append(tz)
            seen.add(tz)
    for tz in all_tz:
        if tz not in seen:
            result.append(tz)
            seen.add(tz)
    return result


def tz_matches(query: str, tz_name: str) -> bool:
    """Return True if *query* matches *tz_name* (case-insensitive, space=underscore)."""
    q = query.lower().replace(" ", "_").replace("-", "_")
    t = tz_name.lower()
    # Match any part of the tz name or just the city portion (after last '/')
    city = t.rsplit("/", 1)[-1]
    region = t.rsplit("/", 1)[0] if "/" in t else ""
    return q in t or q in city or q in region


def convert_to_pkt(source_tz: ZoneInfo, hour: int, minute: int) -> tuple[datetime, int]:
    """
    Convert a wall-clock time (hour, minute) in *source_tz* to PKT today.
    Returns (pkt_datetime, day_offset) where day_offset is -1, 0, or +1.
    """
    now_local = datetime.now(source_tz)
    # Build a datetime with the user's chosen H:M in the source timezone
    src_dt = now_local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    pkt_dt  = src_dt.astimezone(PKT)
    # Day offset relative to *today in source tz*
    offset = (pkt_dt.date() - src_dt.date()).days
    return pkt_dt, offset


def utc_offset_str(tz: ZoneInfo) -> str:
    """Return a human-readable UTC offset like 'UTC+5:30'."""
    now = datetime.now(tz)
    total_minutes = int(now.utcoffset().total_seconds() / 60)
    sign = "+" if total_minutes >= 0 else "-"
    abs_m = abs(total_minutes)
    h, m = divmod(abs_m, 60)
    if m:
        return f"UTC{sign}{h}:{m:02d}"
    return f"UTC{sign}{h}"


# ─── Main Widget ──────────────────────────────────────────────────────────────

class PKTWidget(tk.Tk):

    def __init__(self):
        super().__init__()

        self._all_timezones = sorted_timezones()
        self._source_tz     = ZoneInfo("America/New_York")  # default
        self._drag_x = 0
        self._drag_y = 0
        self._always_on_top = tk.BooleanVar(value=True)
        self._dropdown_open = False

        self._setup_window()
        self._build_ui()
        self._tick()      # start live clock

    # ── Window setup ──────────────────────────────────────────────────────────

    def _setup_window(self):
        self.overrideredirect(True)       # frameless
        self.resizable(False, False)
        self.configure(bg=BG_DARK)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.97)   # slight transparency

        # Centre on screen at startup
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - W) // 2
        y  = (sh - H) // 2
        self.geometry(f"{W}x{H}+{x}+{y}")

        # Drag bindings (bound later to drag_handle canvas)
        self.bind("<Map>", lambda e: self._apply_always_on_top())

    def _apply_always_on_top(self, *_):
        self.attributes("-topmost", self._always_on_top.get())

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Root canvas (rounded illusion via outer frame) ────────────────────
        outer = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        outer.pack(fill="both", expand=True)

        inner = tk.Frame(outer, bg=BG_DARK)
        inner.pack(fill="both", expand=True)

        # ── Title bar / drag handle ───────────────────────────────────────────
        bar = tk.Frame(inner, bg=BG_CARD, height=36)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Flag + title
        flag = tk.Label(bar, text="🇵🇰", bg=BG_CARD, font=(FONT_FACE, 14))
        flag.pack(side="left", padx=(10, 4), pady=4)

        title = tk.Label(
            bar, text="PKT Time Converter",
            bg=BG_CARD, fg=TEXT_PRIMARY,
            font=(FONT_FACE, 11, "bold"),
        )
        title.pack(side="left", pady=4)

        # Controls: pin + close
        close_btn = tk.Label(
            bar, text="✕", bg=BG_CARD, fg=TEXT_SECONDARY,
            font=(FONT_FACE, 11, "bold"), cursor="hand2", padx=8,
        )
        close_btn.pack(side="right", pady=4)
        close_btn.bind("<Button-1>", lambda e: self.destroy())
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg=ACCENT))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg=TEXT_SECONDARY))

        pin_btn = tk.Label(
            bar, text="📌", bg=BG_CARD,
            font=(FONT_FACE, 11), cursor="hand2", padx=6,
        )
        pin_btn.pack(side="right", pady=4)
        pin_btn.bind("<Button-1>", self._toggle_pin)
        pin_btn.bind("<Enter>", lambda e: pin_btn.config(bg=BG_INPUT))
        pin_btn.bind("<Leave>", lambda e: pin_btn.config(bg=BG_CARD))
        self._pin_btn = pin_btn

        # Drag bindings on the whole bar and its children
        for widget in (bar, flag, title):
            widget.bind("<ButtonPress-1>",   self._drag_start)
            widget.bind("<B1-Motion>",        self._drag_move)

        # ── Live PKT Clock ────────────────────────────────────────────────────
        clock_frame = tk.Frame(inner, bg=BG_DARK)
        clock_frame.pack(fill="x", padx=14, pady=(10, 4))

        self._time_label = tk.Label(
            clock_frame, text="",
            bg=BG_DARK, fg=TEXT_PRIMARY,
            font=(FONT_MONO, 32, "bold"),
            anchor="w",
        )
        self._time_label.pack(side="left")

        self._ampm_label = tk.Label(
            clock_frame, text="",
            bg=BG_DARK, fg=ACCENT,
            font=(FONT_FACE, 14, "bold"),
            anchor="sw", pady=8,
        )
        self._ampm_label.pack(side="left", padx=(4, 0))

        self._date_label = tk.Label(
            inner, text="",
            bg=BG_DARK, fg=TEXT_SECONDARY,
            font=(FONT_FACE, 9),
            anchor="w",
        )
        self._date_label.pack(fill="x", padx=16)

        # Thin separator
        sep = tk.Frame(inner, bg=BORDER, height=1)
        sep.pack(fill="x", padx=14, pady=(8, 6))

        # ── Converter section ─────────────────────────────────────────────────
        conv_lbl = tk.Label(
            inner, text="CONVERT TO PKT",
            bg=BG_DARK, fg=TEXT_MUTED,
            font=(FONT_FACE, 7, "bold"),
            anchor="w",
        )
        conv_lbl.pack(fill="x", padx=16)

        # Row 1: TZ search
        row1 = tk.Frame(inner, bg=BG_DARK)
        row1.pack(fill="x", padx=14, pady=(4, 2))

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search_change)

        self._search_entry = tk.Entry(
            row1,
            textvariable=self._search_var,
            bg=BG_INPUT, fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat",
            font=(FONT_FACE, 9),
            bd=0,
        )
        self._search_entry.pack(fill="x", ipady=5, padx=0)
        self._search_entry.insert(0, "America/New_York")
        self._search_entry.bind("<FocusIn>",  self._on_search_focus_in)
        self._search_entry.bind("<FocusOut>", self._on_search_focus_out)
        self._search_entry.bind("<Return>",   self._on_search_return)
        self._search_entry.bind("<Down>",     self._dropdown_down)
        self._search_entry.bind("<Up>",       self._dropdown_up)
        self._search_entry.bind("<Escape>",   self._close_dropdown)

        # Dropdown listbox (overlaying, hidden by default)
        self._dropdown_frame = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        self._listbox = tk.Listbox(
            self._dropdown_frame,
            bg=BG_CARD, fg=TEXT_PRIMARY,
            selectbackground=ACCENT2,
            selectforeground=TEXT_PRIMARY,
            relief="flat", borderwidth=0,
            font=(FONT_FACE, 9),
            height=6,
            activestyle="none",
            highlightthickness=0,
            exportselection=False,
        )
        scrollbar = tk.Scrollbar(self._dropdown_frame, orient="vertical",
                                 command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=scrollbar.set)
        self._listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._listbox.bind("<ButtonRelease-1>", self._on_listbox_select)
        self._listbox.bind("<Return>",          self._on_listbox_select)

        # Row 2: Time input + result
        row2 = tk.Frame(inner, bg=BG_DARK)
        row2.pack(fill="x", padx=14, pady=(4, 2))

        time_lbl = tk.Label(row2, text="Time:", bg=BG_DARK, fg=TEXT_SECONDARY,
                            font=(FONT_FACE, 9), width=5, anchor="w")
        time_lbl.pack(side="left")

        self._hour_var   = tk.StringVar(value="12")
        self._minute_var = tk.StringVar(value="00")
        self._ampm_var   = tk.StringVar(value="PM")

        h_spin = tk.Spinbox(
            row2, from_=1, to=12,
            textvariable=self._hour_var,
            bg=BG_INPUT, fg=TEXT_PRIMARY,
            buttonbackground=BG_INPUT,
            insertbackground=TEXT_PRIMARY,
            relief="flat", font=(FONT_MONO, 10, "bold"),
            width=3, bd=0, wrap=True,
            command=self._on_time_change,
        )
        h_spin.pack(side="left", ipady=4)
        h_spin.bind("<KeyRelease>", lambda e: self._on_time_change())

        tk.Label(row2, text=":", bg=BG_DARK, fg=TEXT_PRIMARY,
                 font=(FONT_MONO, 10, "bold")).pack(side="left")

        m_spin = tk.Spinbox(
            row2, from_=0, to=59,
            textvariable=self._minute_var,
            bg=BG_INPUT, fg=TEXT_PRIMARY,
            buttonbackground=BG_INPUT,
            insertbackground=TEXT_PRIMARY,
            relief="flat", font=(FONT_MONO, 10, "bold"),
            width=3, bd=0, wrap=True, format="%02.0f",
            command=self._on_time_change,
        )
        m_spin.pack(side="left", ipady=4)
        m_spin.bind("<KeyRelease>", lambda e: self._on_time_change())

        ampm_menu = tk.OptionMenu(row2, self._ampm_var, "AM", "PM",
                                  command=lambda _: self._on_time_change())
        ampm_menu.config(
            bg=BG_INPUT, fg=TEXT_PRIMARY,
            activebackground=ACCENT2, activeforeground=TEXT_PRIMARY,
            relief="flat", font=(FONT_FACE, 9), bd=0, padx=4,
            highlightthickness=0,
        )
        ampm_menu["menu"].config(bg=BG_CARD, fg=TEXT_PRIMARY,
                                 activebackground=ACCENT2)
        ampm_menu.pack(side="left", padx=(2, 0))

        # Offset badge
        self._tz_offset_lbl = tk.Label(
            row2, text="",
            bg=BG_DARK, fg=TEXT_MUTED,
            font=(FONT_FACE, 8), anchor="e",
        )
        self._tz_offset_lbl.pack(side="right")

        # Result row
        row3 = tk.Frame(inner, bg=BG_CARD, pady=8)
        row3.pack(fill="x", padx=14, pady=(6, 10))

        pkt_ico = tk.Label(row3, text="→  PKT", bg=BG_CARD, fg=TEXT_MUTED,
                           font=(FONT_FACE, 9, "bold"), padx=10)
        pkt_ico.pack(side="left")

        self._result_label = tk.Label(
            row3, text="—",
            bg=BG_CARD, fg=GREEN,
            font=(FONT_MONO, 16, "bold"),
        )
        self._result_label.pack(side="left", padx=(0, 4))

        self._result_ampm = tk.Label(
            row3, text="",
            bg=BG_CARD, fg=ACCENT,
            font=(FONT_FACE, 10, "bold"),
        )
        self._result_ampm.pack(side="left")

        self._day_offset_label = tk.Label(
            row3, text="",
            bg=BG_CARD, fg=ORANGE,
            font=(FONT_FACE, 8, "bold"),
            anchor="e", padx=6,
        )
        self._day_offset_label.pack(side="right")

        # Trigger initial conversion
        self._on_time_change()

    # ── Drag ──────────────────────────────────────────────────────────────────

    def _drag_start(self, event):
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _drag_move(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.geometry(f"+{x}+{y}")
        self._reposition_dropdown()

    # ── Pin / Always-on-top ───────────────────────────────────────────────────

    def _toggle_pin(self, _event=None):
        current = self._always_on_top.get()
        self._always_on_top.set(not current)
        self.attributes("-topmost", not current)
        self._pin_btn.config(fg="" if not current else ACCENT)

    # ── Live Clock ────────────────────────────────────────────────────────────

    def _tick(self):
        now = datetime.now(PKT)
        time_str = now.strftime("%I:%M:%S").lstrip("0") or "12:00:00"
        ampm_str = now.strftime("%p")
        date_str = now.strftime("%A, %d %B %Y")

        self._time_label.config(text=time_str)
        self._ampm_label.config(text=ampm_str)
        self._date_label.config(text=f"{PKT_LABEL}  ·  {date_str}")

        self.after(1000, self._tick)

    # ── Timezone Search ───────────────────────────────────────────────────────

    def _on_search_focus_in(self, _event=None):
        self._search_entry.select_range(0, "end")
        self._show_dropdown()

    def _on_search_focus_out(self, _event=None):
        # Delay so listbox click is processed first
        self.after(150, self._close_dropdown)

    def _on_search_change(self, *_):
        self._show_dropdown()

    def _on_search_return(self, _event=None):
        if self._listbox.size() > 0:
            self._listbox.selection_clear(0, "end")
            self._listbox.selection_set(0)
            self._on_listbox_select()

    def _dropdown_down(self, _event=None):
        if not self._dropdown_open:
            self._show_dropdown()
            return
        cur = self._listbox.curselection()
        if not cur:
            self._listbox.selection_set(0)
        else:
            idx = min(cur[0] + 1, self._listbox.size() - 1)
            self._listbox.selection_clear(0, "end")
            self._listbox.selection_set(idx)
            self._listbox.see(idx)

    def _dropdown_up(self, _event=None):
        cur = self._listbox.curselection()
        if not cur:
            return
        idx = max(cur[0] - 1, 0)
        self._listbox.selection_clear(0, "end")
        self._listbox.selection_set(idx)
        self._listbox.see(idx)

    def _show_dropdown(self):
        query = self._search_var.get().strip()
        matches = [tz for tz in self._all_timezones if tz_matches(query, tz)][:80]

        self._listbox.delete(0, "end")
        for tz in matches:
            self._listbox.insert("end", tz)

        if not matches:
            self._close_dropdown()
            return

        self._reposition_dropdown()
        self._dropdown_frame.lift()
        self._dropdown_open = True

    def _reposition_dropdown(self):
        self.update_idletasks()
        ex = self._search_entry.winfo_rootx()
        ey = self._search_entry.winfo_rooty() + self._search_entry.winfo_height() + 2
        ew = self._search_entry.winfo_width()
        item_h = max(self._listbox.size(), 1)
        dh = min(item_h, 6) * 18 + 4
        self._dropdown_frame.place(x=ex - self.winfo_rootx(),
                                   y=ey - self.winfo_rooty(),
                                   width=ew, height=dh)

    def _close_dropdown(self, _event=None):
        self._dropdown_frame.place_forget()
        self._dropdown_open = False

    def _on_listbox_select(self, _event=None):
        sel = self._listbox.curselection()
        if not sel:
            return
        tz_name = self._listbox.get(sel[0])
        self._source_tz = ZoneInfo(tz_name)
        self._search_var.set(tz_name)
        self._close_dropdown()
        self._search_entry.icursor("end")
        self._update_tz_offset()
        self._on_time_change()

    def _update_tz_offset(self):
        try:
            offset_str = utc_offset_str(self._source_tz)
            self._tz_offset_lbl.config(text=offset_str)
        except Exception:
            self._tz_offset_lbl.config(text="")

    # ── Time conversion ───────────────────────────────────────────────────────

    def _on_time_change(self, *_):
        try:
            h = int(self._hour_var.get() or 12)
            m = int(self._minute_var.get() or 0)
            ampm = self._ampm_var.get()

            # Clamp
            h = max(1, min(12, h))
            m = max(0, min(59, m))

            # Convert 12h → 24h
            if ampm == "AM":
                h24 = 0 if h == 12 else h
            else:
                h24 = 12 if h == 12 else h + 12

            pkt_dt, day_offset = convert_to_pkt(self._source_tz, h24, m)

            result_time = pkt_dt.strftime("%I:%M").lstrip("0") or "12:00"
            result_ampm = pkt_dt.strftime("%p")

            self._result_label.config(text=result_time)
            self._result_ampm.config(text=result_ampm)

            if day_offset == 0:
                self._day_offset_label.config(text="Same Day", fg=TEXT_MUTED)
            elif day_offset == 1:
                self._day_offset_label.config(text="▲ Next Day", fg=ORANGE)
            elif day_offset == -1:
                self._day_offset_label.config(text="▼ Prev Day", fg=ACCENT2)
            else:
                self._day_offset_label.config(text=f"{day_offset:+d} Days", fg=ORANGE)

            self._update_tz_offset()

        except (ValueError, Exception):
            self._result_label.config(text="—")
            self._result_ampm.config(text="")
            self._day_offset_label.config(text="")


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = PKTWidget()
    app.mainloop()
