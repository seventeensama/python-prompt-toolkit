from __future__ import unicode_literals
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.widgets import YesNoDialog, InputDialog, MessageDialog

__all__ = (
    'yes_no_dialog',
    'input_dialog',
    'message_dialog',
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


def input_dialog(title='', text='', ok_text='OK', cancel_text='Cancel',
                 password=False):
    """
    Display a text input box.
    Return the given text, or None when cancelled.
    """
    def cancel_handler(app):
        app.set_return_value(None)

    def ok_handler(app):
        app.set_return_value(dialog.textfield.text)

    dialog = InputDialog(
        title=title,
        text=text,
        ok_handler=ok_handler,
        cancel_handler=cancel_handler,
        ok_text=ok_text,
        cancel_text=cancel_text,
        password=password)

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


def message_dialog(title='', text=''):
    """
    Display a simple message box and wait until the user presses enter.
    """
    def done(app):
        " Called when 'Enter' is pressed. "
        app.set_return_value(None)

    dialog = MessageDialog(
        title=title,
        text=text,
        ok_handler=done)

    application = Application(
        layout=Layout(dialog),
        key_bindings=merge_key_bindings([
            load_key_bindings(),
        ]),
        mouse_support=True,
        use_alternate_screen=True)

    # Run event loop.
    return application.run()
