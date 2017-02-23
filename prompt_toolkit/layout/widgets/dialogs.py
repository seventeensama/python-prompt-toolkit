"""
Collection of reusable components for building full screen applications.
"""
from __future__ import unicode_literals
import six
from prompt_toolkit.eventloop import EventLoop, get_event_loop
from prompt_toolkit.token import Token
from .base import Box, Shadow, Button, Label, TextArea, Frame, RadioList
from ..containers import VSplit, HSplit

__all__ = (
    'Dialog',
    'InputDialog',
    'MessageDialog',
    'YesNoDialog',
    'RadioListDialog',
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
    def __init__(self, title, body, buttons, loop=None):
        assert loop is None or isinstance(loop, EventLoop)
        assert isinstance(title, six.text_type)
        assert isinstance(buttons, list)

        loop = loop or get_event_loop()

        self.container = Box(
            body=Shadow(
                body=Frame(
                    title=title,
                    body=HSplit([
                        # Wrap the content in a `Box`, so that the Dialog can
                        # be larger than the content.
                        body,
                        # The buttons.
                        Box(body=VSplit(buttons, padding=1))
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
    def __init__(self, title='', text='', password=False, completer=None,
                 ok_handler=None, cancel_handler=None, ok_text='Ok',
                 cancel_text='Cancel', loop=None):
        assert isinstance(title, six.text_type)
        assert isinstance(text, six.text_type)
        assert ok_handler is None or callable(ok_handler)
        assert cancel_handler is None or callable(cancel_handler)
        assert loop is None or isinstance(loop, EventLoop)

        loop = loop or get_event_loop()

        ok_button = Button(loop=loop, text=ok_text, handler=ok_handler)
        cancel_button = Button(loop=loop, text=cancel_text, handler=cancel_handler)

        def accept(app):
            app.layout.focus(ok_button)

        self.textfield = TextArea(
            loop=loop,
            multiline=False,
            password=password,
            completer=completer,
            accept_handler=accept)

        self.dialog = Dialog(
            loop=loop,
            title=title,
            body=HSplit([
                Box(body=Label(loop=loop, text=text)),
                self.textfield,
            ]),
            buttons=[ok_button, cancel_button])

    def __pt_container__(self):
        return self.dialog


class MessageDialog(object):
    """
    A dialog window that displays a message.
    """
    def __init__(self, title='', text='', ok_handler=None, loop=None):
        assert loop is None or isinstance(loop, EventLoop)
        assert isinstance(title, six.text_type)
        assert isinstance(text, six.text_type)
        assert ok_handler is None or callable(ok_handler)

        loop = loop or get_event_loop()

        self.dialog = Dialog(
            loop=loop,
            title=title,
            body=Box(body=Label(loop=loop, text=text)),
            buttons=[
                Button(loop=loop, text='Ok', handler=ok_handler),
            ])

    def __pt_container__(self):
        return self.dialog


class YesNoDialog(object):
    """
    A dialog window with "Yes" and "No" buttons.
    """
    def __init__(self, title='', text='', yes_handler=None, no_handler=None,
                 yes_text='Yes', no_text='No', loop=None):
        assert isinstance(title, six.text_type)
        assert isinstance(text, six.text_type)
        assert yes_handler is None or callable(yes_handler)
        assert no_handler is None or callable(no_handler)
        assert loop is None or isinstance(loop, EventLoop)

        loop = loop or get_event_loop()

        self.dialog = Dialog(
            loop=loop,
            title=title,
            body=Box(body=Label(loop=loop, text=text)),
            buttons=[
                Button(loop=loop, text=yes_text, handler=yes_handler),
                Button(loop=loop, text=no_text, handler=no_handler),
            ])

    def __pt_container__(self):
        return self.dialog


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
            body=Box(body=HSplit([
                Label(loop=loop, text=text),
                self.radio_list,
            ])),
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
