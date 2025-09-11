import shutil
import sys


def progress_bar(current, total):
    """A simple progress bar.

    :param current: progress
    :param total:
    """
    if total == 0:
        return
    # Get terminal width
    terminal_width = shutil.get_terminal_size((80, 20)).columns
    # Leave space for counters and brackets
    bar_length = terminal_width - len(str(total)) * 2 - 4

    progress = current / total
    bar = "=" * int(bar_length * progress) + "-" * (
        bar_length - int(bar_length * progress)
    )
    sys.stdout.write(f"\r[{bar}] {current}/{total}")
    if current == total:
        sys.stdout.write("\n")
    sys.stdout.flush()
