#!/usr/bin/env python
"""
"""
from __future__ import unicode_literals

from functools import partial
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.eventloop.base import EventLoop
from prompt_toolkit.eventloop.defaults import create_event_loop
from prompt_toolkit.filters import Condition, has_focus
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import VSplit, HSplit, Window, Align, to_window, FloatContainer, Float, Container, ConditionalContainer
from prompt_toolkit.layout.controls import BufferControl, TokenListControl, UIControlKeyBindings
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.layout.processors import PasswordProcessor
from prompt_toolkit.styles.from_pygments import style_from_pygments
from prompt_toolkit.token import Token
from prompt_toolkit.utils import get_cwidth
from pygments.lexers import HtmlLexer

loop = create_event_loop()

from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout.widgets import TextArea, Label, Frame, Box, Checkbox, Shadow, InputDialog, MessageDialog, Button, RadioButtonList


class MenuContainer(object):
    def __init__(self, body, menu_items=None):
        assert isinstance(menu_items, list) and \
            all(isinstance(i, MenuItem) for i in menu_items)

        self.body = body
        self.menu_items = menu_items
        self.selected_menu = 0

        # Key bindings.
        kb = KeyBindings()

        @kb.add(Keys.Left)
        def _(event):
            self.selected_menu = (self.selected_menu - 1) % len(self.menu_items)

        @kb.add(Keys.Right)
        def _(event):
            self.selected_menu = (self.selected_menu + 1) % len(self.menu_items)

        @kb.add(Keys.Up)
        def _(event):
            menu = self.menu_items[self.selected_menu]
            menu.selected_item = (menu.selected_item - 1) % len(menu.children)

        @kb.add(Keys.Down)
        def _(event):
            menu = self.menu_items[self.selected_menu]
            menu.selected_item = (menu.selected_item + 1) % len(menu.children)

        # Controls.
        self.control = TokenListControl(
            self._get_menu_tokens,
            key_bindings=kb,
            focussable=True)

        self.window = Window(
            height=1,
            content=self.control,
            token=Token.MenuBar)

        self.container = FloatContainer(
            content=HSplit([
                # The titlebar.
                self.window,

                # The 'body', like defined above.
                body,
            ]),
            floats=[
                Float(xcursor=self.window, ycursor=self.window,#top=1, left=1,
                    content=self._submenu(), transparant=False),
                Float(xcursor=True,
                      ycursor=True,
                      content=CompletionsMenu(
                          max_height=16,
                          scroll_offset=1)
                ),
            ]
        )

    def _get_menu_tokens(self, app):
        result = []
        for i, item in enumerate(self.menu_items):
            result.append((Token.MenuBar, ' '))
            if i == self.selected_menu:
                result.append((Token.SetMenuPosition, ''))
            result.append((Token.Menu, item.text))
        return result

    def _submenu(self):
        def get_tokens(app):
            selected_menu = self.menu_items[self.selected_menu]

            result = []
            for i, item in enumerate(selected_menu.children):
                if i == selected_menu.selected_item:
                    result.append((Token.SetCursorPosition, ''))

                result.append((Token, ' {} '.format(item.text)))

                if i != len(selected_menu.children) - 1:
                    result.append((Token.Menu, '\n'))
            return result

        return ConditionalContainer(
            content=Window(
                TokenListControl(get_tokens),
                cursorline=True,
                token=Token.Menu),
            filter=Condition(lambda app: app.layout.current_window == self.window))

    def __pt_container__(self):
        return self.container


class MenuItem(object):
    def __init__(self, text='', handler=None, children=None, shortcut=None):
        self.text = text
        self.handler = handler
        self.children = children
        self.shortcut = shortcut
        self.selected_item = 0


class ProgressBar(object):
    def __init__(self, loop):
        self.container = FloatContainer(
            content=VSplit([
                Window(token=Token.ProgressBar.Used, height=1, width=D(weight=60)),
                Window(token=Token.ProgressBar, height=1, width=D(weight=40)),
            ]),
            floats=[
                Float(content=Label(loop, '60%'), top=0, bottom=0),
            ])

    def __pt_container__(self):
        return self.container


# >>>

def accept_yes(app):
    app.set_return_value(True)

def accept_no(app):
    app.set_return_value(False)


# Make partials that pass the loop everywhere.
Frame_ = partial(Frame, loop=loop)
Button_ = partial(Button, loop=loop)
Label_ = partial(Label, loop=loop)
TextArea_ = partial(TextArea, loop=loop)
Checkbox_ = partial(Checkbox, loop=loop)
Box_ = partial(Box, loop=loop)
ProgressBar_ = partial(ProgressBar, loop=loop)


yes_button = Button('Yes', handler=accept_yes)
no_button = Button('No', handler=accept_no)
textfield  = TextArea_(lexer=PygmentsLexer(HtmlLexer))
textfield2 = TextArea_()
checkbox1 = Checkbox_(text='Checkbox')
checkbox2 = Checkbox_(text='Checkbox')

radios = RadioButtonList(loop=loop, values=[
    ('Red', 'red'),
    ('Green', 'green'),
    ('Blue', 'blue'),
    ('Orange', 'orange'),
    ('Yellow', 'yellow'),
    ('Purple', 'Purple'),
    ('Brown', 'Brown'),
])

animal_completer = WordCompleter([
    'alligator', 'ant', 'ape', 'bat', 'bear', 'beaver', 'bee', 'bison', 'butterfly', 'cat', 'chicken', 'crocodile', 'dinosaur', 'dog', 'dolphin', 'dove', 'duck', 'eagle', 'elephant', 'fish', 'goat', 'gorilla', 'kangaroo', 'leopard', 'lion', 'mouse', 'rabbit', 'rat', 'snake', 'spider', 'turkey', 'turtle', ], ignore_case=True)



root_container = HSplit([
    VSplit([
        Frame_(body=Label_(text='Left frame\ncontent')),
        InputDialog(
            loop, 'The custom window', 'This is the\nwindow content',
            password=True, completer=animal_completer),
        MessageDialog(loop, 'The custom window',
                      'this is\nthe other window.\nTest')
    ]),
    VSplit([
        Frame_(body=HSplit([
            textfield,
            ProgressBar_(),
        ])),
        #VerticalLine(),
        Frame_(body=HSplit([
            checkbox1,
            checkbox2,
        ], align='TOP')),
        Frame_(body=radios),
    ], padding=1),
    Box_(
        body=VSplit([
            yes_button,
            no_button,
        ], align='CENTER', padding=1),
        padding=1,
        token=Token.Menu,
    ),
])

root_container = MenuContainer(root_container, menu_items=[
    MenuItem('File', children=[
        MenuItem('Open'),
        MenuItem('Save'),
        MenuItem('Save as...'),
        MenuItem('----'),
        MenuItem('Exit'),
        ]),
    MenuItem('Edit', children=[
        MenuItem('Cut'),
        MenuItem('Copy'),
        MenuItem('Paste'),
    ]),
    MenuItem('Info', children=[
        MenuItem('About'),
    ]),
])

# Global key bindings.
bindings = KeyBindings()
bindings.add(Keys.Tab)(focus_next)
bindings.add(Keys.BackTab)(focus_previous)


style = style_from_pygments(style_dict={
    Token.Button.Arrow: 'bold',
    Token.Label: '#888888 reverse',
    Token.Window.Border: '#888888',

    Token.MenuBar: 'bg:#00ff00 #000000',
    Token.Menu: 'bg:#008888 #ffffff',
    Token.DialogTitle: 'bg:#444444 #ffffff',
    Token.DialogBody: 'bg:#888888',
    Token.Menu | Token.CursorLine: 'reverse',
#    Token.Focussed: 'reverse',
    Token.Window.Border|Token.Shadow: 'bg:#ff0000',
    Token.Menu|Token.Shadow: 'bg:#ff0000',
    Token.Dialog: 'bg:#0000ff',
    Token.Dialog | Token.Shadow: 'bg:#000088',

    Token.Focussed | Token.Button: 'bg:#880000 #ffffff noinherit',

    Token.Dialog | Token.Dialog: 'bg:#ffffff #000000',
    Token.Dialog | Token.Frame.Label: '#ff0000 bold',

    Token.Dialog | Token.TextArea: 'bg:#aaaaaa underline',
    Token.Dialog | Token.Button | Token.Focussed: 'bg:#880000 #ffffff',

    Token.ProgressBar: 'bg:#000088',
    Token.ProgressBar.Used: 'bg:#ff0000',

    Token.RadioList | Token.Focussed: 'noreverse',
    Token.RadioList | Token.Focussed | Token.Radio.Selected: 'reverse',
})


application = Application(
    loop=loop,
    layout=Layout(
        root_container,
        focussed_window=yes_button,
    ),
    key_bindings=merge_key_bindings([
        load_key_bindings(),
        bindings,
    ]),
    style=style,
    mouse_support=True,
    use_alternate_screen=True)


def run():
    result = application.run()
    print('You said: %r' % result)


if __name__ == '__main__':
    run()
