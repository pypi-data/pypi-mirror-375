import click
from mosamatic2.commands import (
    calculatescores,
    rescaledicomimages,
    segmentmusclefatl3tensorflow,
    createpngsfromsegmentations,
)
from mosamatic2.core.utils import show_doc_command


class CustomHelpGroup(click.Group):
    def format_commands(self, ctx, formatter):
        commands = self.list_commands(ctx)
        with formatter.section('Commands'):
            for command_name in commands:
                command = self.get_command(ctx, command_name)
                if command is None or command.hidden:
                    continue
                help_text = command.get_short_help_str()
                formatter.write_text(f'{command_name:15} {help_text}')


@click.group(cls=CustomHelpGroup)
def main():
    pass


main.add_command(calculatescores.calculatescores)
main.add_command(rescaledicomimages.rescaledicomimages)
main.add_command(segmentmusclefatl3tensorflow.segmentmusclefatl3tensorflow)
main.add_command(createpngsfromsegmentations.createpngsfromsegmentations)
main.add_command(show_doc_command(main)) # Special command to show long description for command