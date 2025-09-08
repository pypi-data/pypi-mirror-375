from tkinter import ttk

from period_tracker.data import load_entries
from period_tracker.gui.calendar_view import setup_calendar, update_calendar_tags
from period_tracker.gui.summary import setup_summary, display_summary
from period_tracker.gui.entry_controls import setup_entry_controls, refresh_entry_list


class PeriodTrackerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Period and Fertility Tracker v0.1.1")

        self.entries = load_entries()

        self.setup_layout()

        display_summary(self)
        refresh_entry_list(self)
        update_calendar_tags(self)

    def setup_layout(self):
        self.left_frame = ttk.Frame(self.root, padding=10)
        self.left_frame.pack(side="left", fill="y")

        self.center_frame = ttk.Frame(self.root, padding=10)
        self.center_frame.pack(side="left", fill="both", expand=True)

        self.right_frame = ttk.Frame(self.root, padding=10)
        self.right_frame.pack(side="right", fill="y")

        setup_calendar(self)
        setup_summary(self)
        setup_entry_controls(self)
