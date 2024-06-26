import click
from openctp_ctp_channels import channels


@click.group()
def main():
    ...


@click.command(help="Check channel info.")
def check():
    ...


@click.command(help="Switch channel.")
@click.argument("channel")
def switch(channel):
    # bak
    # replace
    # todo
    if 'tts' == channel:
        channel = channels.TTSChannel()
        channel.download()
        channel.switch()
    elif 'ctp' == channel:
        channel = channels.CTPChannel()
        channel.switch()


@click.command('channels', help="Show supported channels.")
def show_channels():
    print("Support channels:", " | ".join(channels.CHANNELS))


main.add_command(check)
main.add_command(switch)
main.add_command(show_channels)
