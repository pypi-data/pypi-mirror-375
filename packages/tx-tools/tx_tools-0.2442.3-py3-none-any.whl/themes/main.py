from pathlib import Path
from sys import argv
from textwrap import dedent

from themes.app import Themes


def main():
    try:
        assert len(argv) == 2, f'usage : {argv[0].split("/")[-1]} {{file}}'
        path = Path(argv[1])
        assert path.is_file(), f'file not found : {path}'
        app = Themes(path)
        theme = app.run()
        print(theme)
    except Exception as x:
        print(f'''
        ! {x}
        ''')


if __name__ == '__main__': main()
