"""
Collection of reusable components for building full screen applications.
"""
from __future__ import unicode_literals
from functools import partial

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.eventloop.base import EventLoop
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.token import Token
from prompt_toolkit.utils import get_cwidth

from ..containers import Window, VSplit, HSplit, FloatContainer, Float, Align
from ..controls import BufferControl, TokenListControl
from ..dimension import Dimension as D
from ..processors import PasswordProcessor
from ..margins import ScrollbarMargin


__all__ = (
    'TextArea',
    'Label',
    'Button',
    'Frame',
    'Shadow',
    'Box',
    'VerticalLine',
    'HorizontalLine',
    'RadioButtonList',

    'Checkbox',  # XXX: refactor into CheckboxList.
)


class BORDER:
    " Box drawing characters. (Thin) "
    HORIZONTAL = '\u2500'
    VERTICAL = '\u2502'
    TOP_LEFT = '\u250c'
    TOP_RIGHT = '\u2510'
    BOTTOM_LEFT = '\u2514'
    BOTTOM_RIGHT = '\u2518'
    #LIGHT_VERTICAL = '\u2501'


class WIDE_BORDER:
    " Box drawing characters. (Wide) "
    HORIZONTAL = '\u2501'
    VERTICAL = '\u2503'
    TOP_LEFT = '\u250f'
    TOP_RIGHT = '\u2513'
    BOTTOM_LEFT = '\u2517'
    BOTTOM_RIGHT = '\u251b'
    #LIGHT_VERTICAL = '\u2502'


class SHADE:
    LIGHT = '\u9617'
    MEDIUM = '\u9618'
    DARK = '\u9619'


class TextArea(object):
    """
    A simple input field.

    :param multiline: If True, allow multiline input.
    :param password: When `True`, display using asteriks.
    """
    def __init__(self, loop, multiline=True, password=False,
                 lexer=None, completer=None):
        assert isinstance(loop, EventLoop)

        if password:
            processor = PasswordProcessor()
        else:
            processor = None

        self.buffer = Buffer(
            loop=loop,
            multiline=multiline,
            completer=completer,
            complete_while_typing=True)

        self.control = BufferControl(
            buffer=self.buffer,
            lexer=lexer,
            input_processor=processor)

        height = D() if multiline else D.exact(1)

        self.window = Window(
            height=height,
            content=self.control,
            token=Token.TextArea,
            wrap_lines=True)

    def __pt_container__(self):
        return self.window


class Label(object):
    """
    Widget that displays the given text.
    """
    def __init__(self, loop, text, token=None, width=None):
        assert isinstance(loop, EventLoop)

        if width is None:
            longest_line = max(get_cwidth(line) for line in text.splitlines())
            width = D.exact(longest_line)

        self.buffer = Buffer(loop=loop, document=Document(text, 0))
        self.buffer_control = BufferControl(self.buffer, focussable=False)
        self.window = Window(content=self.buffer_control, token=token, width=width)

    def __pt_container__(self):
        return self.window


class Button(object):
    """
    :param text: The caption for the button.
    :param handler: `None` or callable. Called when the button is clicked.
    :param width: Width of the button.
    """
    def __init__(self, text, handler=None, width=12):
        assert handler is None or callable(handler)
        assert isinstance(width, int)

        self.text = text
        self.handler = handler
        self.width = width
        self.control = TokenListControl(
            self._get_tokens,
            key_bindings=self._get_key_bindings(),
            focussable=True)

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
            (token.Arrow, '<', self.handler),
            (token.Text, text, self.handler),
            (token.Arrow, '>', self.handler),
        ]

    def _get_key_bindings(self):
        kb = KeyBindings()
        @kb.add(' ')
        @kb.add(Keys.Enter)
        def _(event):
            if self.handler is not None:
                self.handler(event.app)

        return kb

    def __pt_container__(self):
        return self.window


class Frame(object):
    """
    Draw a border around any container.

    :param body: Another container object.
    """
    def __init__(self, loop, body, title='', token=None):
        assert isinstance(loop, EventLoop)

        fill = partial(Window, token=Token.Window.Border)

        if title:
            top_row = VSplit([
                fill(width=1, height=1, char=BORDER.TOP_LEFT),
                fill(char=BORDER.HORIZONTAL),
                fill(width=1, height=1, char='|'),
                Label(loop, ' {} '.format(title), token=Token.Frame.Label),
                fill(width=1, height=1, char='|'),
                fill(char=BORDER.HORIZONTAL),
                fill(width=1, height=1, char=BORDER.TOP_RIGHT),
            ])
        else:
            top_row = VSplit([
                fill(width=1, height=1, char=BORDER.TOP_LEFT),
                fill(char=BORDER.HORIZONTAL),
                fill(width=1, height=1, char=BORDER.TOP_RIGHT),
            ])

        self.container = HSplit([
            top_row,
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
    """
    Draw a shadow underneath/behind this container.
    (This applies `Token.Shadow` the the cells under the shadow. The Style
    should define the colors for the shadow.)
    """
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

    This also makes sure that the parent can reverse more space than required by
    the child. This is very useful when wrapping a small element with a fixed
    size into a ``VSplit`` or ``HSplit`` object. The ``HSplit`` and ``VSplit``
    tries to make sure to adapt respectively the width and height, possibly
    shrinking other elements. Wrapping something in a ``Box``, makes it flexible.
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


class Checkbox(object):
    def __init__(self, loop, text):
        self.checked = True

        kb = KeyBindings()

        @kb.add(' ')
        @kb.add(Keys.Enter)
        def _(event):
            self.checked = not self.checked

        self.control = TokenListControl(
            self._get_tokens,
            key_bindings=kb,
            focussable=True)

        self.window = Window(width=3, content=self.control)

        self.container = VSplit([
            self.window,
            Label(loop=loop, text=' {}'.format(text))
        ])

    def _get_tokens(self, app):
        text = '*' if self.checked else ' '
        return [(Token, '[%s]' % text)]

    def __pt_container__(self):
        return self.container


class RadioButtonList(object):
    """
    :param values: List of (label, value) tuples.
    """
    def __init__(self, loop, values):
        assert isinstance(values, list)
        assert len(values) > 0
        assert all(isinstance(i, tuple) and len(i) == 2
                   for i in values)

        self.values = values
        self.current_value = values[0][1]
        self._selected_index = 0

        # Key bindings.
        kb = KeyBindings()
        @kb.add(Keys.Up)
        def _(event):
            self._selected_index = max(0, self._selected_index - 1)

        @kb.add(Keys.Down)
        def _(event):
            self._selected_index = min(
                len(self.values) - 1, self._selected_index + 1)

        @kb.add(Keys.Enter)
        @kb.add(' ')
        def _(event):
            self.current_value = self.values[self._selected_index][1]

        # Control and window.
        self.control = TokenListControl(
            self._get_tokens,
            key_bindings=kb,
            focussable=True)

        self.window = Window(
            content=self.control,
            token=Token.RadioList,
            right_margins=[
                ScrollbarMargin(display_arrows=True),
            ])

    def _get_tokens(self, app):
        result = []
        for i, value in enumerate(self.values):
            checked = (value[1] == self.current_value)
            selected = (i == self._selected_index)

            token = Token
            if checked:
                token |= Token.Radio.Checked
            if selected:
                token |= Token.Radio.Selected

            result.append((token, '('))

            if selected:
                result.append((Token.SetCursorPosition, ''))

            if checked:
                result.append((token, '*'))
            else:
                result.append((token, ' '))

            result.append((token, ')'))
            result.append((Token.Radio, ' '))
            result.append((Token.Radio, value[0]))
            result.append((Token, '\n'))

        return result

    def __pt_container__(self):
        return self.window


class VerticalLine(object):
    """
    A simple vertical line with a width of 1.
    """
    def __init__(self):
        self.window = Window(
            char=BORDER.VERTICAL,
            token=Token.Line,
            width=1)

    def __pt_container__(self):
        return self.window


class HorizontalLine(object):
    """
    A simple horizontal line with a height of 1.
    """
    def __init__(self):
        self.window = Window(
            char=BORDER.HORIZONTAL,
            token=Token.Line,
            height=1)

    def __pt_container__(self):
        return self.window
