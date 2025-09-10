from textwrap import dedent
from sys import argv

from maker.commands import edit_conf, make


def usage(arg):
    cmd = argv[0].split('/')[-1]
    arg = ' '.join(arg)
    if arg != 'help': print(f' ! {cmd} {arg} ')
    print(dedent(f'''
        {cmd}
            Run the main tui.

        {cmd} command
            Run {{command}}.

        {cmd} command help
            Get help for {{command}}.


    commands:
        help
        config
    '''))


def main():
    match argv[1:]:
        case ['config', *arg]:
            edit_conf(arg)
        case [] | None:
            make()
        case invalid:
            usage(invalid)


if __name__ == "__main__": main()
