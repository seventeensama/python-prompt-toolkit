#!/usr/bin/env python
"""
Example of confirmation dialog window.
"""
from __future__ import unicode_literals
from prompt_toolkit.shortcuts.dialogs import message_dialog


def main():
    message_dialog(
        title='Example dialog window',
        text='Do you want to confirm?')


if __name__ == '__main__':
    main()
