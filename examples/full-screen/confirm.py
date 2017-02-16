"""
Example of confirmation dialog window.
"""
from __future__ import unicode_literals
from prompt_toolkit.application import Application
from prompt_toolkit.eventloop.defaults import create_event_loop
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.widgets import YesNoDialog


def main():
    loop = create_event_loop()

    # UI.
    def yes_handler(app):
        app.set_return_value(True)

    def no_handler(app):
        app.set_return_value(False)

    dialog = YesNoDialog(
        loop,
        title='Example dialog window',
        text='Do you want to confirm?',
        yes_handler=yes_handler,
        no_handler=no_handler)

    # Key bindings.
    bindings = KeyBindings()
    bindings.add(Keys.Tab)(focus_next)
    bindings.add(Keys.BackTab)(focus_previous)

    application = Application(
        loop=loop,
        layout=Layout(dialog),
        key_bindings=merge_key_bindings([
            load_key_bindings(),
            bindings,
        ]),
        mouse_support=True,
        use_alternate_screen=True)

    # Run event loop.
    result = application.run()

    # Print result.
    print('Result = {}'.format(result))


if __name__ == '__main__':
    main()
