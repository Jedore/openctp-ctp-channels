import click
from openctp_ctp_channels import channels


@click.group()
def main():
    pass


@click.command(help="Check channel info.")
def check():
    channel = channels.CTPChannel()
    print('Current channel:', channel.current_channel())


@click.command(help="Switch channel.")
@click.argument("channel")
def switch(channel):
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
