#!/usr/bin/env python
"""
"""
from __future__ import unicode_literals

from functools import partial
from prompt_toolkit.application import Application
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.eventloop.defaults import create_event_loop
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import VSplit, HSplit, Window, FloatContainer, Float, ConditionalContainer
from prompt_toolkit.layout.controls import TokenListControl
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout.widgets import TextArea, Label, Frame, Box, Checkbox, InputDialog, MessageDialog, Button, RadioButtonList, Shadow
from prompt_toolkit.layout.widgets.base import BORDER
from prompt_toolkit.styles.from_pygments import style_from_pygments
from prompt_toolkit.token import Token
from prompt_toolkit.utils import get_cwidth
from pygments.lexers import HtmlLexer


loop = create_event_loop()

class MenuContainer(object):
    def __init__(self, body, menu_items=None):
        assert isinstance(menu_items, list) and \
            all(isinstance(i, MenuItem) for i in menu_items)

        self.body = body
        self.menu_items = menu_items
        self.selected_menu = [0]

        # Key bindings.
        kb = KeyBindings()

        @Condition
        def in_main_menu(app):
            return len(self.selected_menu) == 1

        @Condition
        def in_sub_menu(app):
            return len(self.selected_menu) > 1

        # Navigation through the main menu.

        @kb.add(Keys.Left, filter=in_main_menu)
        def _(event):
            self.selected_menu[0] = max(0, self.selected_menu[0] - 1)

        @kb.add(Keys.Right, filter=in_main_menu)
        def _(event):
            self.selected_menu[0] = min(
                len(self.menu_items) - 1, self.selected_menu[0] + 1)

        @kb.add(Keys.Down, filter=in_main_menu)
        def _(event):
            self.selected_menu.append(0)

        # Sub menu navigation.

#        @kb.add(Keys.Escape, filter=in_sub_menu, eager=True)
        @kb.add(Keys.Left, filter=in_sub_menu)
        def _(event):
            " Go back to parent menu. "
            if len(self.selected_menu) > 1:
                self.selected_menu.pop()

        @kb.add(Keys.Right, filter=in_sub_menu)
        def _(event):
            " go into sub menu. "
            if self._get_menu(len(self.selected_menu) - 1).children:
                self.selected_menu.append(0)

            # If This item does not have a sub menu. Go up in the parent menu.
            elif len(self.selected_menu) == 2 and self.selected_menu[0] < len(self.menu_items) - 1:
                self.selected_menu = [min(
                    len(self.menu_items) - 1, self.selected_menu[0] + 1)]
                if self.menu_items[self.selected_menu[0]].children:
                    self.selected_menu.append(0)

        @kb.add(Keys.Up, filter=in_sub_menu)
        def _(event):
            if len(self.selected_menu) == 2 and self.selected_menu[1] == 0:
                self.selected_menu.pop()
            else:
                self.selected_menu[-1] -= 1

        @kb.add(Keys.Down, filter=in_sub_menu)
        def _(event):
            if self.selected_menu[-1] < len(self._get_menu(len(self.selected_menu) - 2).children) - 1:
                self.selected_menu[-1] += 1

#        @kb.add(Keys.Enter)
#        def _(event):
#            " Click the selected menu item. "
#            menu = self.menu_items[self.selected_menu]
#            item = menu.children[menu.selected_item]
#            if item.handler:
#                item.handler()

        # Controls.
        self.control = TokenListControl(
            self._get_menu_tokens,
            key_bindings=kb,
            focussable=True)

        self.window = Window(
            height=1,
            content=self.control,
            token=Token.MenuBar)

        submenu = self._submenu(0)
        submenu2 = self._submenu(1)
        submenu3 = self._submenu(2)

        @Condition
        def has_focus(app):
            return app.layout.current_window == self.window


        self.container = FloatContainer(
            content=HSplit([
                # The titlebar.
                self.window,

                # The 'body', like defined above.
                body,
            ]),
            floats=[
                Float(xcursor=self.window, ycursor=self.window,
                      content=ConditionalContainer(
                          content=Shadow(loop, body=submenu),
                          filter=has_focus)),
                Float(attach_to_window=submenu,
                      xcursor=True, ycursor=True,
                      content=ConditionalContainer(
                          content=Shadow(loop, body=submenu2),
                          filter=has_focus & Condition(lambda app: len(self.selected_menu) >= 1))),
                Float(attach_to_window=submenu2,
                      xcursor=True, ycursor=True,
                      content=ConditionalContainer(
                          content=Shadow(loop, body=submenu3),
                          filter=has_focus & Condition(lambda app: len(self.selected_menu) >= 2))),

                # --
                Float(xcursor=True,
                      ycursor=True,
                      content=CompletionsMenu(
                          max_height=16,
                          scroll_offset=1)),
            ]
        )

    def _get_menu(self, level):
        menu = self.menu_items[self.selected_menu[0]]

        for i, index in enumerate(self.selected_menu[1:]):
            if i < level:
                try:
                    menu = menu.children[index]
                except IndexError:
                    return MenuItem('debug')

        return menu

    def _get_menu_tokens(self, app):
        result = []
        focussed = (app.layout.current_window == self.window)

        for i, item in enumerate(self.menu_items):
            result.append((Token.MenuBar, ' '))
            if i == self.selected_menu[0] and focussed:
                result.append((Token.SetMenuPosition, ''))
                token = Token.MenuBar.SelectedItem
            else:
                token = Token.MenuBar
            result.append((token, item.text))
        return result

    def _submenu(self, level=0):
        def get_tokens(app):
            result = []
            if level < len(self.selected_menu):
                menu = self._get_menu(level)
                if menu.children:
                    result.append((Token.Menu, BORDER.TOP_LEFT))
                    result.append((Token.Menu, BORDER.HORIZONTAL * (menu.width + 4)))
                    result.append((Token.Menu, BORDER.TOP_RIGHT))
                    result.append((Token, '\n'))
                    try:
                        selected_item = self.selected_menu[level + 1]
                    except IndexError:
                        selected_item = -1

                    for i, item in enumerate(menu.children):
                        if i == selected_item:
                            result.append((Token.SetCursorPosition, ''))
                            token = Token.MenuBar.SelectedItem
                        else:
                            token = Token

                        result.append((Token.Menu, BORDER.VERTICAL))
                        if set(item.text) == {'-'}:
                            result.append((token | Token.Menu.Border, '{}'.format(BORDER.HORIZONTAL * (menu.width + 3))))
                        else:
                            result.append((token, ' {}'.format(item.text).ljust(menu.width + 3)))

                        if item.children:
                            result.append((token, '>'))
                        else:
                            result.append((token, ' '))

                        if i == selected_item:
                            result.append((Token.SetMenuPosition, ''))
                        result.append((Token.Menu, BORDER.VERTICAL))

                        result.append((Token, '\n'))

                    result.append((Token.Menu, BORDER.BOTTOM_LEFT))
                    result.append((Token.Menu, BORDER.HORIZONTAL * (menu.width + 4)))
                    result.append((Token.Menu, BORDER.BOTTOM_RIGHT))
            return result

        return Window(
                    TokenListControl(get_tokens),
                    token=Token.Menu,
                    transparent=False)

    def __pt_container__(self):
        return self.container


class MenuItem(object):
    def __init__(self, text='', handler=None, children=None, shortcut=None,
                 disabled=False):
        self.text = text
        self.handler = handler
        self.children = children or []
        self.shortcut = shortcut
        self.disabled = disabled
        self.selected_item = 0

    @property
    def width(self):
        if self.children:
            return max(get_cwidth(c.text) for c in self.children)
        else:
            return 0


class ProgressBar(object):
    def __init__(self, loop):
        self.container = FloatContainer(
            content=Window(height=1),
            floats=[
                # We first draw the label, than the actual progress bar.  Right
                # now, this is the only way to have the colors of the progress
                # bar appear on to of the label. The problem is that our label
                # can't be part of any `Window` below.
                Float(content=Label(loop, '60%'), top=0, bottom=0),

                Float(left=0, top=0, right=0, bottom=0, content=VSplit([
                    Window(token=Token.ProgressBar.Used, width=D(weight=60)),
                    Window(token=Token.ProgressBar, width=D(weight=40)),
                ])),
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
        ], align='BOTTOM', padding=1),
        padding=1,
        token=Token.Buttonbar,
    ),
])

root_container = MenuContainer(root_container, menu_items=[
    MenuItem('File', children=[
        MenuItem('New'),
        MenuItem('Open', children=[
            MenuItem('From file...'),
            MenuItem('From URL...'),
            MenuItem('Something else..', children=[
                MenuItem('A'),
                MenuItem('B'),
                MenuItem('C'),
                MenuItem('D'),
                MenuItem('E'),
            ]),
        ]),
        MenuItem('Save'),
        MenuItem('Save as...'),
        MenuItem('-', disabled=True),
        MenuItem('Exit'),
        ]),
    MenuItem('Edit', children=[
        MenuItem('Undo'),
        MenuItem('Cut'),
        MenuItem('Copy'),
        MenuItem('Paste'),
        MenuItem('Delete'),
        MenuItem('-', disabled=True),
        MenuItem('Find'),
        MenuItem('Find next'),
        MenuItem('Replace'),
        MenuItem('Go To'),
        MenuItem('Select All'),
        MenuItem('Time/Date'),
    ]),
    MenuItem('View', children=[
        MenuItem('Status Bar'),
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
    Token.Button: '',
    Token.Button.Arrow: 'bold',
    Token.Label: '#888888 reverse',
    Token.Window.Border: '#888888',
    Token.Shadow: 'bg:#222222',

    Token.MenuBar: 'bg:#aaaaaa #888888',
    Token.MenuBar.SelectedItem: 'bg:#ffffff #000000',
    Token.Menu: 'bg:#888888 #ffffff',
    Token.Menu.Border: '#aaaaaa',
    Token.Window.Border|Token.Shadow: '#444444',

    Token.Dialog: 'bg:#4444ff',
    Token.Dialog | Token.Shadow: 'bg:#000088',
    Token.Dialog.Body: 'bg:#ffffff #000000',
    Token.Dialog.Body | Token.Shadow: 'bg:#aaaaaa',

    Token.Focussed | Token.Button: 'bg:#880000 #ffffff noinherit',

    Token.Dialog | Token.Frame.Label: '#ff0000 bold',

    Token.Dialog.Body | Token.TextArea: 'bg:#cccccc underline',
    Token.Dialog.Body | Token.Button | Token.Focussed: 'bg:#880000 #ffffff',

    Token.ProgressBar: 'bg:#000088',
    Token.ProgressBar.Used: 'bg:#ff0000',

    Token.RadioList | Token.Focussed: 'noreverse',
    Token.RadioList | Token.Focussed | Token.Radio.Selected: 'reverse',

    Token.Buttonbar: 'bg:#aaaaff'
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
