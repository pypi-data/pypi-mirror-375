import tkinter as tk
from tkcalendar import Calendar
from datetime import datetime, timedelta

from period_tracker.logic import get_starts, avg_cyc, avg_period, forecast_windows


def setup_calendar(ui):
    """Create and pack the calendar widget with tag labels."""
    ui.calendar = Calendar(ui.center_frame, selectmode="none")
    ui.calendar.pack(fill="both", expand=True, padx=10, pady=10)

    # Legend
    for label, color in [
        ("Past Period", "red"),
        ("Predicted Period", "pink"),
        ("Fertile Window", "blue"),
        ("Ovulation Day", "purple"),
    ]:
        box = tk.Label(ui.center_frame, bg=color, width=2, height=1, relief="raised")
        text = tk.Label(ui.center_frame, text=label, padx=5)
        box.pack(side="left", padx=2)
        text.pack(side="left", padx=2)

    # Tag color configuration
    ui.calendar.tag_config("period", background="red", foreground="white")
    ui.calendar.tag_config("predicted_period", background="pink", foreground="black")
    ui.calendar.tag_config("fertile", background="blue", foreground="white")
    ui.calendar.tag_config("ovulation", background="purple", foreground="white")


def update_calendar_tags(ui):
    """Clear old calendar tags and apply new ones based on entry data."""
    for tag in ["period", "fertile", "ovulation", "predicted_period"]:
        ui.calendar.calevent_remove(tag=tag)

    dates = get_starts(ui.entries)
    if not dates:
        return

    try:
        luteal_phase_len = int(ui.luteal_phase_entry.get())
    except ValueError:
        luteal_phase_len = 14  # fallback

    avg_cycle = avg_cyc(dates)
    last_date = dates[-1]
    entries = ui.entries

    # Tag actual period days
    for e in entries:
        start = datetime.strptime(e["start"], "%Y-%m-%d").date()
        end = datetime.strptime(e["end"], "%Y-%m-%d").date()
        for i in range((end - start).days + 1):
            ui.calendar.calevent_create(start + timedelta(days=i), "", "period")

    avg_len = avg_period(entries)

    # Tag future predicted windows
    for fw in forecast_windows(last_date, avg_cycle, luteal_phase_len=luteal_phase_len):
        for i in range((fw["fertile_end"] - fw["fertile_start"]).days + 1):
            ui.calendar.calevent_create(
                fw["fertile_start"] + timedelta(days=i), "", "fertile"
            )
        ui.calendar.calevent_create(fw["ovulation_day"], "", "ovulation")
        for i in range(avg_len):
            ui.calendar.calevent_create(
                fw["next_period"] + timedelta(days=i), "", "predicted_period"
            )
