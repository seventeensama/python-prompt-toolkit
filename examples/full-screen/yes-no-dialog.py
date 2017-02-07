#!/usr/bin/env python
"""
"""
from __future__ import unicode_literals

from functools import partial
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.eventloop.defaults import create_event_loop
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import VSplit, HSplit, Window, Align, to_window, FloatContainer, Float, Container, ConditionalContainer
from prompt_toolkit.layout.controls import BufferControl, TokenListControl, UIControlKeyBindings
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.styles.from_pygments import style_from_pygments
from prompt_toolkit.token import Token
from prompt_toolkit.filters import Condition
from prompt_toolkit.utils import get_cwidth
from prompt_toolkit.eventloop.base import EventLoop
from pygments.lexers import HtmlLexer

loop = create_event_loop()


class BORDER:
    " Box drawing characters. "
    HORIZONTAL = '\u2501'
    VERTICAL = '\u2503'
    TOP_LEFT = '\u250f'
    TOP_RIGHT = '\u2513'
    BOTTOM_LEFT = '\u2517'
    BOTTOM_RIGHT = '\u251b'
    LIGHT_VERTICAL = '\u2502'


class TextArea(object):
    def __init__(self, loop, text=''):
        assert isinstance(loop, EventLoop)

        self.buffer = Buffer(loop=loop)

        self.window = Window(
            content=BufferControl(buffer=self.buffer, lexer=PygmentsLexer(HtmlLexer)),
            token=Token.TextArea,
            #align=Align.CENTER,
            wrap_lines=True)

    def __pt_container__(self):
        return self.window


class Label(object):
    """
    Widget that displays the given text.
    """
    def __init__(self, loop, text, token=None):
        assert isinstance(loop, EventLoop)

        if '\n' in text:
            width = D()
        else:
            width = D.exact(get_cwidth(text))

        self.buffer = Buffer(loop=loop, document=Document(text, 0))
        self.buffer_control = BufferControl(self.buffer)
        self.window = Window(content=self.buffer_control, token=token, width=width)

    def __pt_container__(self):
        return self.window


class Frame(object):
    """
    Draw a border around a container.
    """
    def __init__(self, loop, body, title='', token=None):
        assert isinstance(loop, EventLoop)

        fill = partial(Window, token=Token.Window.Border)

        self.container = HSplit([
            VSplit([
                fill(width=1, height=1, char=BORDER.TOP_LEFT),
                fill(char=BORDER.HORIZONTAL),
                fill(width=1, height=1, char='|'),
                Label(loop, ' {} '.format(title), token=Token.Frame.Label),
                fill(width=1, height=1, char='|'),
                fill(char=BORDER.HORIZONTAL),
                fill(width=1, height=1, char=BORDER.TOP_RIGHT),
            ]),
            VSplit([
                fill(width=1, char=BORDER.VERTICAL),
                body,
                fill(width=1, char=BORDER.VERTICAL),
            ]),
            VSplit([
                fill(width=1, height=1, char=BORDER.BOTTOM_LEFT),
                fill(char=BORDER.HORIZONTAL),
                fill(width=1, height=1, char=BORDER.BOTTOM_RIGHT),
            ]),
        ], token=token)

    def __pt_container__(self):
        return self.container


class Shadow(object):
    def __init__(self, loop, body):
        self.container = FloatContainer(
            content=body,
            floats=[
                Float(bottom=-1, height=1, left=1, right=-1,
                    content=Window(token=Token.Shadow)),
                Float(bottom=-1, top=1, width=1, right=-1,
                    content=Window(token=Token.Shadow)),
                ]
            )

    def __pt_container__(self):
        return self.container


class Box(object):
    """
    Add padding around a container.
    """
    def __init__(self, loop, body, padding=0,
                 padding_left=None, padding_right=None,
                 padding_top=None, padding_bottom=None,
                 token=None, char=None):
        def get(value):
            return value if value is not None else padding

        self.padding_left = get(padding_left)
        self.padding_right = get(padding_right)
        self.padding_top = get(padding_top)
        self.padding_bottom = get(padding_bottom)
        self.body = body

        self.container = HSplit([
            Window(height=D(min=self.padding_top), char=char),
            VSplit([
                Window(width=D(min=self.padding_left), char=char),
                body,
                Window(width=D(min=self.padding_right), char=char),
            ]),
            Window(height=D(min=self.padding_bottom), char=char),
        ], token=token)

    def __pt_container__(self):
        return self.container


class CheckBox(object):
    def __init__(self, loop, text):
        self.checked = True

        kb = KeyBindings()

        @kb.add(' ')
        @kb.add(Keys.Enter)
        @kb.add('p')
        def _(event):
            self.checked = not self.checked

        self.control = TokenListControl(
            self._get_checkbox_tokens,
            get_key_bindings=lambda app: UIControlKeyBindings(kb, modal=False))

        self.window = Window(width=3, content=self.control)

        self.container = VSplit([
            self.window,
            Label(loop=loop, text=text)
        ])

    def _get_checkbox_tokens(self, app):
        text = 'x' if self.checked else ' '
        return [
            (Token, '[%s]' % text)
        ]

    def __pt_container__(self):
        return self.container


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
            get_key_bindings=lambda app: UIControlKeyBindings(kb, modal=False))

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
                Float(xcursor=True, ycursor=True,#top=1, left=1,
                    content=self._submenu(), transparant=False),
#                Float(content=dialog()),
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


class Button(object):
    def __init__(self, text, action=None, width=12):
        assert action is None or callable(action)
        assert isinstance(width, int)

        self.text = text
        self.action = action
        self.width = width
        self.control = TokenListControl(
            self._get_tokens,
            get_key_bindings=self._get_key_bindings)

        self.window = Window(
            self.control,
            align=Align.CENTER,
            height=1,
            width=width,
            token=Token.Button,
            dont_extend_width=True,
            dont_extend_height=True)

    def _get_tokens(self, app):
        token = Token.Button
        text = ('{:^%s}' % (self.width - 2)).format(self.text)

        return [
            (token.Arrow, '<'),
            (token.Text, text),
            (token.Arrow, '>'),
        ]

    def _get_key_bindings(self, app):
        kb = KeyBindings()
        @kb.add(' ')
        @kb.add(Keys.Enter)
        def _(event):
            if self.action is not None:
                self.action(app)

        return UIControlKeyBindings(kb, modal=False)

    def __pt_container__(self):
        return self.window


class VerticalLine(object):
    def __init__(self):
        self.window = Window(
            char=BORDER.VERTICAL,
            token=Token.Line,
            width=1)

    def __pt_container__(self):
        return self.window


class HorizontalLine(object):
    def __init__(self):
        self.window = Window(
            char=BORDER.HORIZONTAL,
            token=Token.Line,
            height=1)

    def __pt_container__(self):
        return self.window

# >>>


def create_pane():
    return Window()


def accept_yes(app):
    app.set_return_value(True)

def accept_no(app):
    app.set_return_value(False)


# Make partials that pass the loop everywhere.
Frame_ = partial(Frame, loop=loop)
Button_ = partial(Button, loop=loop)
Label_ = partial(Label, loop=loop)
TextField_ = partial(TextArea, loop=loop)
CheckBox_ = partial(CheckBox, loop=loop)
Box_ = partial(Box, loop=loop)


yes_button = Button('Yes', action=accept_yes)
no_button = Button('No', action=accept_no)
textfield = TextField_()
textfield2 = TextField_()
checkbox1 = CheckBox_(text='Checkbox')
checkbox2 = CheckBox_(text='Checkbox')

root_container = HSplit([
    VSplit([
#        Frame_(title='Test', body=Label('hello world\ntest')),
        Frame_(body=Label_(text='Left frame\ncontent')),
        Box_(
            body=Shadow(loop,
                Frame_(
                    title='The custom window',
                    body=HSplit([
                        Label_(text='right frame\ncontent'),
                        Box_(
                            body=VSplit([
                                Button('Yes'),
                                Button('No'),
                            ], padding=1),
                        )
                    ]),
                    token=Token.Dialog)),
            padding=3,
            token=Token.RightTopPane,
        )
    ]),
    VSplit([
        Frame_(body=textfield),
        #VerticalLine(),
        Frame_(body=VSplit([
            HSplit([
                checkbox1,
                checkbox2,
            ], align='TOP'),
        ])),
        Frame_(body=textfield2),
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

widgets = [to_window(w) for w in
    (yes_button, no_button, textfield, textfield2)
] + [checkbox1.window, checkbox2.window, root_container.window]


@bindings.add(Keys.Tab)
def _(event):
    index = widgets.index(event.app.layout.current_window)
    index = (index + 1) % len(widgets)
    event.app.layout.focus(widgets[index])

@bindings.add(Keys.BackTab)
def _(event):
    index = widgets.index(event.app.layout.current_window)
    index = (index - 1) % len(widgets)
    event.app.layout.focus(widgets[index])


style = style_from_pygments(style_dict={
    Token.Button.Arrow: 'bold',
    Token.Label: '#888888 reverse',
    Token.Window.Border: '#888888',

    Token.MenuBar: 'bg:#00ff00 #000000',
    Token.Menu: 'bg:#008888 #ffffff',
    Token.DialogTitle: 'bg:#444444 #ffffff',
    Token.DialogBody: 'bg:#888888',
    Token.CursorLine: 'reverse',
    Token.Focussed: 'reverse',
    #Token.Shadow: '#ff0000 underline noinherit',
   # Token.Menu| 
    #Token.Window.Border|
    Token.Window.Border|Token.Shadow: 'bg:#ff0000',
    Token.Menu|Token.Shadow: 'bg:#ff0000',
    Token.RightTopPane: 'bg:#0000ff',
    Token.RightTopPane | Token.Shadow: 'bg:#000088',

    Token.Focussed | Token.Button: 'bg:#ff0000 noinherit',

    Token.RightTopPane | Token.Dialog: 'bg:#ffffff #000000',
    Token.RightTopPane | Token.Frame.Label: '#ff0000 bold',
})


application = Application(
    loop=loop,
    layout=Layout(root_container, focussed_window=yes_button.__pt_container__()),
    key_bindings=merge_key_bindings([
        load_key_bindings(),
        bindings,
    ]),
    style=style,

    # Let's add mouse support!
    mouse_support=True,

    # Using an alternate screen buffer means as much as: "run full screen".
    # It switches the terminal to an alternate screen.
    use_alternate_screen=True)


def run():
    result = application.run()
    print('You said: %r' % result)


if __name__ == '__main__':
    run()
