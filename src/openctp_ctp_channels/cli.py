import click
from openctp_ctp_channels import channels


@click.group()
def main():
    pass


@click.command(help="Show current channel.")
def check():
    channel = channels.CTPChannel()
    print('Current channel:', channel.current_channel())


@click.command(help="Switch channel.")
@click.argument("channel")
def switch(channel):
    if 'tts' == channel:
        channel = channels.TTSChannel()
        channel.switch()
    elif 'ctp' == channel:
        channel = channels.CTPChannel()
        channel.switch()


@click.command(help="Show all channels.")
def show():
    print("Support channels:")
    for channel, name in channels.CHANNELS.items():
        print(f"\t{channel} - {name}")


main.add_command(check)
main.add_command(switch)
main.add_command(show)
