from rich.syntax import Syntax
from rich.traceback import Traceback
from textual import on
from textual.app import App
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Static

from pybrary.makelib import parse
from tx_widgets import SelectFuzzy


class Main(Screen):
    CSS = '''
        #targets{
            width: 1fr;
        }
        #preview{
            width: 3fr;
        }
    '''

    def compose(self):
        try:
            self.makefile = parse()
        except FileNotFoundError:
            self.exit(message='\n ! makefile not found')
        with Horizontal():
            yield SelectFuzzy(self.makefile.keys(), id='targets')
            yield Static(id="preview", expand=True)

    def on_mount(self, event):
        self.query_one('#targets').focus()

    @on(SelectFuzzy.UpdateHighlighted)
    def highlight(self, event):
        event.stop()
        name = event.value
        target = self.makefile[name]
        target = f'{name}:\n'+'\n'.join(target)
        preview = self.query_one("#preview", Static)
        theme = self.app.config.theme
        try:
            syntax = Syntax(
                target,
                'makefile',
                line_numbers=False,
                word_wrap=False,
                indent_guides=False,
                theme=theme,
            )
            preview.update(syntax)
            self.query_one("#preview").scroll_home(animate=False)
        except Exception:
            preview.update(Traceback(theme=theme, width=None))
            self.sub_title = "ERROR"

    @on(SelectFuzzy.UpdateSelected)
    def select(self, event):
        event.stop()
        selected = event.value
        cmd = f'make {selected}' if selected else None
        self.app.exit(cmd)
