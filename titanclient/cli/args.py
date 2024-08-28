import click
from collections import OrderedDict

global_params = [
    click.core.Option(
        ("--verbose", "-v"),
        is_flag=True,
        help="verbose output")]


class GlobalArgumentCommand(click.core.Command):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for i, o in enumerate(global_params):
            self.params.insert(i, o)


class NaturalOrderGroup(click.Group):

    def __init__(self, name=None, commands=None, **attrs):
        if commands is None:
            commands = OrderedDict()
        elif not isinstance(commands, OrderedDict):
            commands = OrderedDict(commands)
        click.Group.__init__(self, name=name,
                             commands=commands,
                             **attrs)

    def list_commands(self, ctx):
        return self.commands.keys()
