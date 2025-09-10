from pygments import lexers
from pygments.styles import get_all_styles
from pygments.util import ClassNotFound
from rich.syntax import Syntax
from rich.traceback import Traceback
from textual import on
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Static, OptionList
from textual.widgets.option_list import Option


class Main(Screen):
    CSS = '''
        #styles{
            width: 3fr;
        }
        #preview{
            width: 9fr;
        }
    '''
    BINDINGS = [
        ("escape", "exit", "Exit"),
    ]

    def compose(self):
        styles = [
            Option(style, style)
            for style in get_all_styles()
        ]
        with Horizontal():
            self.themes = OptionList(*styles, id='styles')
            yield self.themes
            self.preview =  Static(id="preview", expand=True)
            yield self.preview

    def on_mount(self, event):
        self.themes.focus()

    def on_key(self, event):
        if event.key == 'delete':
            self.themes.remove_option(self.theme)
            self.themes.action_cursor_down()
            self.themes.action_cursor_up()

    @on(OptionList.OptionHighlighted, '#styles')
    def highlight(self, event):
        event.stop()
        self.theme = event.option.prompt
        path = self.app.path
        try:
            content = open(path).read()
        except Exception as x:
            content = f'{x}'
            file_type = None
        try:
            lexer = lexers.guess_lexer_for_filename(path, content)
            file_type = lexer.name
        except ClassNotFound:
            file_type = None
        syntax = Syntax(
            content,
            file_type,
            line_numbers = True,
            word_wrap = False,
            indent_guides = False,
            theme = self.theme,
        )
        self.preview.update(syntax)
        self.preview.scroll_home(animate=False)

    def action_exit(self):
        self.app.exit(self.theme)
