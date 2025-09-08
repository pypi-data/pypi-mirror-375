from tkinter import ttk
from period_tracker.logic import get_starts, predict, analyse, forecast_windows


def setup_summary(ui):
    """Create and pack the summary label widget."""
    ui.summary_label = ttk.Label(ui.right_frame, text="", justify="left")
    ui.summary_label.pack()


def display_summary(ui):
    """Generate and display the current period and fertility summary."""
    dates = get_starts(ui.entries)
    if not dates:
        ui.summary_label.config(text="No data available.")
        return

    try:
        luteal_phase_len = int(ui.luteal_phase_entry.get())
    except ValueError:
        luteal_phase_len = 14  # fallback default

    avg, next_period, fertile, last_date = predict(
        ui.entries, luteal_phase_len=luteal_phase_len
    )
    stats = analyse(ui.entries)
    future = forecast_windows(last_date, avg, luteal_phase_len=luteal_phase_len)

    summary = (
        f"Next period: {next_period}\n\n"
        f"Cycle stats:\n"
        f" - Avg: {stats['avg']} days\n"
        f" - Range: {stats['min']} to {stats['max']} days\n"
        f" - Std Dev: {stats['std_dev']} days\n\n"
        f"Upcoming Fertile Windows:\n"
    )

    for fw in future:
        summary += (
            f"Cycle {fw['cycle']}: {fw['fertile_start']} to {fw['fertile_end']} "
            f"(Ovulation ~{fw['ovulation_day']})\n"
        )

    ui.summary_label.config(text=summary)
