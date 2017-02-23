from __future__ import unicode_literals
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.widgets import YesNoDialog, InputDialog, MessageDialog, RadioListDialog

__all__ = (
    'yes_no_dialog',
    'input_dialog',
    'message_dialog',
    'radiolist_dialog',
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


def _run_dialog(dialog):
    " Turn the `Dialog` into an `Application` and run it. "
    # Key bindings.
    bindings = KeyBindings()
    bindings.add(Keys.Tab)(focus_next)
    bindings.add(Keys.BackTab)(focus_previous)

    application = Application(
        layout=Layout(dialog),
        key_bindings=merge_key_bindings([
            load_key_bindings(),
            bindings,
        ]),
        mouse_support=True,
        use_alternate_screen=True)

    # Run event loop.
    return application.run()


def _return_none(app):
    " Button handler that returns None. "
    app.set_return_value(None)
