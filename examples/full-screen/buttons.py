#!/usr/bin/env python
"""
A simple example of a few buttons and click handlers.
"""
from __future__ import unicode_literals
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import VSplit, HSplit, Layout
from prompt_toolkit.layout.widgets import Button, Box, TextArea, Label, Frame
from prompt_toolkit.styles.from_dict import style_from_dict
from prompt_toolkit.token import Token


# Event handlers for all the buttons.
def button1_clicked(app):
    text_area.text = 'Button 1 clicked'


def button2_clicked(app):
    text_area.text = 'Button 2 clicked'


def button3_clicked(app):
    text_area.text = 'Button 3 clicked'


def exit_clicked(app):
    app.set_return_value(None)


# All the widgets for the UI.
button1 = Button('Button 1', handler=button1_clicked)
button2 = Button('Button 2', handler=button2_clicked)
button3 = Button('Button 3', handler=button3_clicked)
button4 = Button('Exit', handler=exit_clicked)
text_area = TextArea(focussable=True)


# Combine all the widgets in a UI.
# The `Box` object ensures that padding will be inserted around the containing
# widget. It adapts automatically, unless an explicit `padding` amount is given.
root_container = Box(
    HSplit([
        Label(text='Press `Tab` to move the focus.'),
        VSplit([
            Box(
                body=HSplit(
                    [button1, button2, button3, button4],
                    padding=1),
                padding=1,
                token=Token.LeftPane),
            Box(
                body=Frame(text_area),
                padding=1,
                token=Token.RightPane),
        ]),
    ]),
)

layout = Layout(
    container=root_container,
    focussed_window=button1)


# Key bindings.
kb = KeyBindings()
kb.add(Keys.Tab)(focus_next)
kb.add(Keys.BackTab)(focus_previous)


# This step is not necessary for this application.
#   This will merge our own key bindings with the basic built-in key bindings.
#   Probably, this is what you want if you plan to add editable text fields and
#   you want people to actually be able to edit them. (I'm adding this, because
#   otherwise it could take some time to figure out why editing doesn't work.)
kb = merge_key_bindings([
    load_key_bindings(),
    kb,
])


# Styling.
style = style_from_dict({
    Token.LeftPane: 'bg:#888800 #000000',
    Token.RightPane: 'bg:#00aa00 #000000',
    Token.Button: '#000000',
    Token.Button.Arrow: '#000000',
})


# Build a main application object.
application = Application(
    layout=layout,
    key_bindings=kb,
    style=style,
    use_alternate_screen=True)


def main():
    application.run()


if __name__ == '__main__':
    main()
