from __future__ import unicode_literals
from prompt_toolkit.application import Application
from prompt_toolkit.eventloop import get_event_loop
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout.widgets import YesNoDialog, InputDialog, MessageDialog, RadioListDialog, ProgressBar, Dialog, Button, Label, Box, TextArea
from prompt_toolkit.layout.containers import HSplit

__all__ = (
    'yes_no_dialog',
    'input_dialog',
    'message_dialog',
    'radiolist_dialog',
    'progress_dialog',
)


def yes_no_dialog(title='', text='', yes_text='Yes', no_text='No'):
    """
    Display a Yes/No dialog.
    Return a boolean.
    """
    def yes_handler(app):
        app.set_return_value(True)

    def no_handler(app):
        app.set_return_value(False)

    dialog = YesNoDialog(
        title=title,
        text=text,
        yes_handler=yes_handler,
        no_handler=no_handler,
        yes_text=yes_text,
        no_text=no_text)

    return _run_dialog(dialog)


def input_dialog(title='', text='', ok_text='OK', cancel_text='Cancel',
                 password=False):
    """
    Display a text input box.
    Return the given text, or None when cancelled.
    """
    def ok_handler(app):
        app.set_return_value(dialog.textfield.text)

    dialog = InputDialog(
        title=title,
        text=text,
        ok_handler=ok_handler,
        cancel_handler=_return_none,
        ok_text=ok_text,
        cancel_text=cancel_text,
        password=password)

    return _run_dialog(dialog)


def message_dialog(title='', text=''):
    """
    Display a simple message box and wait until the user presses enter.
    """
    return _run_dialog(MessageDialog(
        title=title,
        text=text,
        ok_handler=_return_none))


def radiolist_dialog(title='', text='', values=None):
    """
    Display a simple message box and wait until the user presses enter.
    """
    def ok_handler(app):
        app.set_return_value(dialog.current_value)

    dialog = RadioListDialog(
        title=title,
        text=text,
        values=values,
        ok_handler=ok_handler,
        cancel_handler=_return_none)

    return _run_dialog(dialog)


def progress_dialog(title='', text='', run_callback=None, loop=None):
    """
    :param run_callback: A function that receives as input a `set_percentage`
        function and it does the work.
    """
    assert callable(run_callback)

    loop = loop or get_event_loop()
    progressbar = ProgressBar()
    text_area = TextArea(loop=loop, focussable=False)

    dialog = Dialog(
        title,
        body=HSplit([
            Box(Label(loop=loop, text=text)),
            Box(text_area, padding=D.exact(1)),
            progressbar,
        ]),
        loop=loop)
    app = _create_app(dialog)

    def set_percentage(value):
        progressbar.percentage = int(value)
        app.invalidate()

    def log_text(text):
        text_area.buffer.insert_text(text)
        app.invalidate()

    # Run the callback in the executor. When done, set a return value for the
    # UI, so that it quits.
    def start():
        try:
            run_callback(set_percentage, log_text)
        finally:
            app.set_return_value(None)

    loop.run_in_executor(start)

    return app.run()


def _run_dialog(dialog):
    " Turn the `Dialog` into an `Application` and run it. "
    application = _create_app(dialog)
    return application.run()


def _create_app(dialog):
    # Key bindings.
    bindings = KeyBindings()
    bindings.add(Keys.Tab)(focus_next)
    bindings.add(Keys.BackTab)(focus_previous)

    return Application(
        layout=Layout(dialog),
        key_bindings=merge_key_bindings([
            load_key_bindings(),
            bindings,
        ]),
        mouse_support=True,
        use_alternate_screen=True)


def _return_none(app):
    " Button handler that returns None. "
    app.set_return_value(None)
