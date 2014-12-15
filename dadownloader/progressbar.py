import sys

def progressBar(label, current, total):
    """
    A simple progress bar for the terminal

    This will print a progress bar to the terminal that looks like:

        <label> [||||      ] 40%

    It is designed to be used for a discrete finite set of tasks to complete.
    You should call progressBar after each task is complete, and not print
    anything else out to the terminal untill all tasks are complete.

    :param str label: Text to print before the progress bar.
    :param int current: The current task number you are performing.
    :param int total: The total number of tasks to complete.
    """
    # Calculate fraction of completed tasks as float
    completion  = float(current)/total

    # Render progress bar and metadata
    progressbar = '|' * int(round(completion*30))
    sys.stdout.write('\r%-20.20s [%-30.30s] %3d%% (%i/%i)' % (
        label, progressbar, int(round(completion*100)), current, total
    ))
    sys.stdout.flush()

    # Write newline after progress bar if all task are complete
    if current == total:
        sys.stdout.write('\n')
        sys.stdout.flush()
