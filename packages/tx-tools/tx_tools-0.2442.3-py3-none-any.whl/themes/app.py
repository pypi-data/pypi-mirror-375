from textual.app import App

from themes.scr import Main


class Themes(App):
    SCREENS = {
        'main': Main,
    }

    def __init__(self, path):
        super().__init__()
        self.path = path

    def on_mount(self, event):
        self.push_screen('main')

