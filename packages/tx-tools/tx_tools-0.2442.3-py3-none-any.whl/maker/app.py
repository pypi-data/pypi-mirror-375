from textual.app import App

from maker.screen import Main


class Maker(App):
    SCREENS = {
        'main': Main,
    }
    BINDINGS = [
        ("q, escape", "quit", "Quit"),
    ]

    def __init__(self, config):
        super().__init__()
        self.config = config

    def on_mount(self, event):
        self.push_screen('main')

