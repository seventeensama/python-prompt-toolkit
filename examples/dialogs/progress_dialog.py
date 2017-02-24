#!/usr/bin/env python
from __future__ import unicode_literals
from prompt_toolkit.shortcuts.dialogs import progress_dialog
import time
import os


def worker(set_percentage, log_text):
    percentage = 0
    for dirpath, dirnames, filenames in os.walk('../..'):
        for f in filenames:
            log_text('{} / {}\n'.format(dirpath, f))
            set_percentage(percentage + 1)
            percentage += 1
            time.sleep(.2)

            if percentage == 100: break
        if percentage == 100: break

    time.sleep(1)


def main():
    progress_dialog(
        title='Progress dialog example',
        text='As an examples, we walk through the filesystem and print all directories',
        run_callback=worker)


if __name__ == '__main__':
    main()
