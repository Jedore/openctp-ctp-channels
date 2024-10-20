import click
from openctp_ctp_channels import channels, __about__


@click.group()
@click.version_option(version=__about__.__version__)
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
    elif 'tts-s' == channel:
        channel = channels.TTSSimuChannel()
    elif 'ctp' == channel:
        channel = channels.CTPChannel()
    elif 'qq' == channel:
        channel = channels.QQChannel()
    elif 'sina' == channel:
        channel = channels.SinaChannel()
    elif 'emt' == channel:
        channel = channels.EMTChannel()
    elif 'xtp' == channel:
        channel = channels.XTPChannel()
    elif 'tora' == channel:
        channel = channels.ToraChannel()
    else:
        print("Unsupported channel!")
        print("\tRefer https://github.com/Jedore/openctp-ctp-channels#%E6%94%AF%E6%8C%81%E9%80%9A%E9%81%93")
        return

    channel.switch()


@click.command(help="Show all channels.")
def show():
    print("Support channels:")
    for channel, name in channels.CHANNELS.items():
        print(f"\t{channel} - {name}")


main.add_command(check)
main.add_command(switch)
main.add_command(show)
