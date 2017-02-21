"""
Collection of reusable components for building full screen applications.
"""
from __future__ import unicode_literals
import six
from prompt_toolkit.eventloop.base import EventLoop
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
    """
    Simple dialog window. This is the base for `InputDialog`, `MessageDialog`
    and `YesNoDialog`.

    :param loop: The `EventLoop` to be used.
    :param title: Text to be displayed at the top of the dialog.
    :param body: Another container object.
    :param buttons: A list of `Button` widgets, displayed at the bottom.
    """
    def __init__(self, loop, title, body, buttons):
        assert isinstance(loop, EventLoop)
        assert isinstance(title, six.text_type)
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
                        body,
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
    """
    A dialog window with one text input field.
    """
    def __init__(self, loop, title='', text='', password=False,
                 completer=None, ok_handler=None, cancel_handler=None):
        assert isinstance(loop, EventLoop)
        assert isinstance(title, six.text_type)
        assert isinstance(text, six.text_type)
        assert ok_handler is None or callable(ok_handler)
        assert cancel_handler is None or callable(cancel_handler)

        self.textfield = TextArea(
            loop=loop,
            multiline=False,
            password=password,
            completer=completer)

        self.dialog = Dialog(
            loop=loop,
            title=title,
            body=HSplit([
                Box(loop=loop,
                    body=Label(loop=loop, text=text)),
                self.textfield,
            ]),
            buttons=[
                Button(loop=loop, text='Ok', handler=ok_handler),
                Button(loop=loop, text='Cancel', handler=cancel_handler),
            ])

    def __pt_container__(self):
        return self.dialog


class MessageDialog(object):
    """
    A dialog window that displays a message.
    """
    def __init__(self, loop, title='', text='', ok_handler=None):
        assert isinstance(loop, EventLoop)
        assert isinstance(title, six.text_type)
        assert isinstance(text, six.text_type)
        assert ok_handler is None or callable(ok_handler)

        self.dialog = Dialog(
            loop=loop,
            title=title,
            body=Box(loop=loop, body=Label(loop=loop, text=text)),
            buttons=[
                Button(loop=loop, text='Ok', handler=ok_handler),
            ])

    def __pt_container__(self):
        return self.dialog


class YesNoDialog(object):
    """
    A dialog window with "Yes" and "No" buttons.
    """
    def __init__(self, loop, title='', text='', yes_handler=None, no_handler=None):
        assert isinstance(loop, EventLoop)
        assert isinstance(title, six.text_type)
        assert isinstance(text, six.text_type)
        assert yes_handler is None or callable(yes_handler)
        assert no_handler is None or callable(no_handler)

        self.dialog = Dialog(
            loop=loop,
            title=title,
            body=Box(loop, body=Label(loop=loop, text=text)),
            buttons=[
                Button(loop=loop, text='Yes', handler=yes_handler),
                Button(loop=loop, text='no', handler=no_handler),
            ])

    def __pt_container__(self):
        return self.dialog
