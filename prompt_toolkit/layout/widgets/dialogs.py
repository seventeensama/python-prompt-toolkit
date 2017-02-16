"""
Collection of reusable components for building full screen applications.
"""
from __future__ import unicode_literals
from prompt_toolkit.token import Token
from .base import Box, Shadow, Button, Label, TextArea, Frame
from ..containers import VSplit, HSplit

__all__ = (
    'Dialog',
    'InputDialog',
    'MessageDialog',
    'YesNoDialog',
)


class Dialog(object):
    def __init__(self, loop, title, body, buttons):
        assert isinstance(buttons, list)

        self.container = Box(
            loop=loop,
            body=Shadow(
                loop=loop,
                body=Frame(
                    loop=loop,
                    title=title,
                    body=HSplit([
                        # Wrap the content in a `Box`, so that the Dialog can
                        # be larger than the content.
                        Box(
                            loop=loop,
                            body=body,
                        ),
                        # The buttons.
                        Box(
                            loop=loop,
                            body=VSplit(buttons, padding=1),
                        )
                    ]),
                    token=Token.Dialog.Body)),
            padding=3,
            token=Token.Dialog)

    def __pt_container__(self):
        return self.container


class InputDialog(object):
    def __init__(self, loop, title='', text='', password=False,
                 completer=None, ok_handler=None, cancel_handler=None):
        self.textfield = TextArea(
            loop=loop,
            multiline=False,
            password=password,
            completer=completer)

        self.dialog = Dialog(
            loop=loop,
            title=title,
            body=HSplit([
                Label(loop=loop, text=text),
                self.textfield,
            ]),
            buttons=[
                Button('Ok', handler=ok_handler),
                Button('Cancel', handler=cancel_handler),
            ])

    def __pt_container__(self):
        return self.dialog


class MessageDialog(object):
    def __init__(self, loop, title='', text='', ok_handler=None):
        self.dialog = Dialog(
            loop=loop,
            title=title,
            body=HSplit([
                Label(loop=loop, text=text),
            ]),
            buttons=[
                Button('Ok', handler=ok_handler),
            ])

    def __pt_container__(self):
        return self.dialog


class YesNoDialog(object):
    def __init__(self, loop, title='', text='', yes_handler=None, no_handler=None):
        self.dialog = Dialog(
            loop=loop,
            title=title,
            body=HSplit([
                Label(loop=loop, text=text),
            ]),
            buttons=[
                Button('Yes', handler=yes_handler),
                Button('no', handler=no_handler),
            ])

    def __pt_container__(self):
        return self.dialog
