from subprocess import call

from textwrap import dedent

from pybrary import Config

from maker.app import Maker
from maker.config import defaults


config = Config('tx_make', defaults)


def edit_conf(arg=None):
    def hlp():
        print(dedent('''config:
            Edit config.
        '''))

    match arg:
        case [] | None:
            config.edit()
        case _:
            hlp()


def make():
    maker = Maker(config)
    cmd = maker.run()
    if cmd:
        print(cmd)
        call(cmd.split())
