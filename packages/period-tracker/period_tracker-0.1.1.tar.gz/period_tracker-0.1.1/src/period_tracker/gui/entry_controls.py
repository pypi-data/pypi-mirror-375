import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

from tkcalendar import DateEntry

from period_tracker.config import load_luteal_phase, save_luteal_phase
from period_tracker.data import save_period, load_entries, write_entries
from period_tracker.gui.summary import display_summary
from period_tracker.gui.calendar_view import update_calendar_tags


def setup_entry_controls(ui):
    """Initialize input widgets and listbox with edit/delete buttons."""
    # --- Entry form (left panel) ---
    tk.Label(ui.left_frame, text="Start Date:").pack(anchor="w")
    ui.start_date = DateEntry(ui.left_frame, width=12)
    ui.start_date.pack()

    tk.Label(ui.left_frame, text="Duration (days):").pack(anchor="w")
    ui.duration_entry = ttk.Entry(ui.left_frame)
    ui.duration_entry.insert(0, "5")
    ui.duration_entry.pack()

    tk.Label(ui.left_frame, text="Luteal Phase Length (days):").pack(anchor="w")
    ui.luteal_phase_entry = ttk.Entry(ui.left_frame)
    ui.luteal_phase_entry.insert(0, str(load_luteal_phase()))
    ui.luteal_phase_entry.pack()

    ttk.Button(ui.left_frame, text="Save Entry", command=lambda: add_entry(ui)).pack(
        pady=5, fill="x"
    )

    # --- Entry list + buttons (right panel) ---
    ui.entry_listbox = tk.Listbox(ui.right_frame, height=6)
    ui.entry_listbox.pack(side="left", fill="x", expand=True)

    btn_frame = ttk.Frame(ui.right_frame)
    btn_frame.pack(fill="x", expand=True)
    tk.Button(btn_frame, text="Edit", command=lambda: update_entry(ui)).pack(
        side="left", padx=5
    )
    tk.Button(btn_frame, text="Delete", command=lambda: delete_entry(ui)).pack(
        side="right", padx=5
    )


def refresh_entry_list(ui):
    """Refresh the listbox to show updated entries."""
    ui.entry_listbox.delete(0, tk.END)
    entries = sorted(ui.entries, key=lambda x: x["start"])
    for e in entries:
        ui.entry_listbox.insert(tk.END, f"{e['start']} to {e['end']}")


def add_entry(ui):
    """Add a new period entry from the form."""
    try:
        start = ui.start_date.get_date()
        duration = int(ui.duration_entry.get())
        luteal_phase_len = int(ui.luteal_phase_entry.get())
        save_period(start, duration)
        save_luteal_phase(luteal_phase_len)
        ui.entries = load_entries()
        refresh_ui(ui)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def delete_entry(ui):
    """Delete the selected period entry."""
    idx = ui.entry_listbox.curselection()
    if not idx or not messagebox.askyesno("Confirm Delete", "Delete this entry?"):
        return
    del ui.entries[idx[0]]
    write_entries(ui.entries)
    ui.entries = load_entries()
    refresh_ui(ui)


def update_entry(ui):
    """Edit the selected period entry."""
    idx = ui.entry_listbox.curselection()
    if not idx:
        return

    entry = ui.entries[idx[0]]

    new_start = simpledialog.askstring(
        "Edit Start Date", "YYYY-MM-DD:", initialvalue=entry["start"]
    )
    new_end = simpledialog.askstring(
        "Edit End Date", "YYYY-MM-DD:", initialvalue=entry["end"]
    )

    if new_start is None or new_end is None:
        return

    try:
        start = datetime.strptime(new_start, "%Y-%m-%d").date()
        end = datetime.strptime(new_end, "%Y-%m-%d").date()
        if end < start:
            raise ValueError("End date cannot be before start date.")
        ui.entries[idx[0]] = {
            "start": start.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
        }
        write_entries(ui.entries)
        ui.entries = load_entries()
        refresh_ui(ui)
    except Exception as e:
        messagebox.showerror("Invalid Input", str(e))


def refresh_ui(ui):
    refresh_entry_list(ui)
    update_calendar_tags(ui)
    display_summary(ui)
