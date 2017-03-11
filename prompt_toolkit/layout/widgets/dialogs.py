"""
Collection of reusable components for building full screen applications.
"""
from __future__ import unicode_literals
import six
from prompt_toolkit.eventloop import EventLoop, get_event_loop
from prompt_toolkit.token import Token
from .base import Box, Shadow, Button, Label, Frame, RadioList
from ..containers import VSplit, HSplit
from ..dimension import Dimension as D

__all__ = (
    'Dialog',
    'RadioListDialog',
)


class Dialog(object):
    """
    Simple dialog window. This is the base for input dialogs, message dialogs
    and confirmation dialogs.

    :param loop: The `EventLoop` to be used.
    :param title: Text to be displayed at the top of the dialog.
    :param body: Another container object.
    :param buttons: A list of `Button` widgets, displayed at the bottom.
    """
    def __init__(self, title, body, buttons=None, loop=None):
        assert loop is None or isinstance(loop, EventLoop)
        assert isinstance(title, six.text_type)
        assert buttons is None or isinstance(buttons, list)

        loop = loop or get_event_loop()
        buttons = buttons or []

        if buttons:
            frame_body = HSplit([
                # Wrap the content in a `Box`, so that the Dialog can
                # be larger than the content.
                Box(body=body, padding=1),
                # The buttons.
                Box(body=VSplit(buttons, padding=1), height=3)
            ])
        else:
            frame_body = body

        self.container = Box(
            body=Shadow(
                body=Frame(
                    title=title,
                    body=frame_body,
                    token=Token.Dialog.Body)),
            padding=D(min=3),
            token=Token.Dialog)

    def __pt_container__(self):
        return self.container


class RadioListDialog(object):
    """
    A dialog window that displays a list of radio buttons.

    :param values: List of (label, value) tuples.
    """
    def __init__(self, values, title='', text='', ok_handler=None,
                 cancel_handler=None, ok_text='Ok', cancel_text='Cancel',
                 loop=None):
        assert isinstance(title, six.text_type)
        assert isinstance(text, six.text_type)
        assert ok_handler is None or callable(ok_handler)
        assert cancel_handler is None or callable(cancel_handler)
        assert loop is None or isinstance(loop, EventLoop)

        loop = loop or get_event_loop()

        self.radio_list = RadioList(values, loop=loop)
        self.dialog = Dialog(
            loop=loop,
            title=title,
            body=HSplit([
                Label(loop=loop, text=text, dont_extend_height=True),
                self.radio_list,
            ], padding=1),
            buttons=[
                Button(loop=loop, text=ok_text, handler=ok_handler),
                Button(loop=loop, text=cancel_text, handler=cancel_handler),
            ])

    @property
    def current_value(self):
        " The value of the currently selected option. "
        return self.radio_list.current_value

    def __pt_container__(self):
        return self.dialog
