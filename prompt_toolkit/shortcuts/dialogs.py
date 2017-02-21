from __future__ import unicode_literals
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.widgets import YesNoDialog

__all__ = (
    'yes_no_dialog',
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
        title='Example dialog window',
        text='Do you want to confirm?',
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
