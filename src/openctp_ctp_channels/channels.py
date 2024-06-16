import abc
import pathlib
import re
import sys
from hashlib import md5

import openctp_ctp
import requests

CHANNELS = ('tts',)

BASE_DIR = pathlib.Path(__file__).parent


class Channel(abc.ABC):

    def __init__(self):
        self._openctp_version = openctp_ctp.__version__
        self._ctp_version = '.'.join(self._openctp_version.split('.')[:3])
        self._platform = ''

        self._channel = ''
        self._base_url = 'https://ctp-channels.jedore.top'
        self._channel_url = ''
        self._version_url = ''
        self._platform_url = ''

        self._channel_dir = pathlib.Path()
        self._tmp_dir = BASE_DIR / '_tmp'
        self.check_tmp_dir()

    @property
    def channel(self):
        return self._channel

    @staticmethod
    def check_openctp_ctp():
        # todo require version
        pass

    def check_platform(self):
        # behind check_openctp_ctp
        if sys.platform.startswith('win32'):
            if sys.maxsize == 0x7FFFFFFF:
                # 32bit
                self._platform = "win32"

            elif sys.maxsize == 0x7FFFFFFFFFFFFFFF:
                # 64bit
                self._platform = "win64"
            else:
                print("Unsupported windows arch!")
                exit(-1)

        elif sys.platform.startswith('linux'):
            self._platform = 'linux64'

    def check_tmp_dir(self):
        if not self._tmp_dir.exists():
            self._tmp_dir.mkdir(exist_ok=True)

    def check_channel_dir(self):
        if not self._channel_dir.exists():
            self._channel_dir.mkdir(exist_ok=True)

    def download_lib(self, name: str, md5_string: str):
        file = self._channel_dir / name
        if file.exists():
            print('Already downloaded:', name)
            return

        url = self._platform_url + name
        print('Download:', url)
        rsp = requests.get(url)
        if 200 != rsp.status_code:
            raise Exception(f'Download {name} failed: '
                            f'{rsp.status_code} {rsp.text}')
        # check md5
        if md5_string != md5(rsp.content).hexdigest():
            raise Exception('md5 check failed')

        # save lib
        with open(file, 'wb') as f:
            f.write(rsp.content)

    def download_libs(self):
        rsp = requests.get(self._platform_url)
        if 200 != rsp.status_code:
            raise Exception(f'Parse libs failed: '
                            f'{rsp.status_code} {rsp.text}')

        text = rsp.text
        for line in text.split('\n'):
            if 'class="lib"' not in line:
                continue

            ret = re.match(r'^.*>(.+\.dll)</a> +(\w+)$', line)
            name = ret.group(1)
            md5_string = ret.group(2)
            self.download_lib(name, md5_string)

    def download(self):
        self.check_openctp_ctp()
        self.check_platform()
        self.generate_url()
        self.check_channel_dir()
        self.download_libs()

    def generate_url(self):
        self._channel_url = self._base_url + '/' + self._channel
        self._version_url = self._channel_url + '/' + self._ctp_version
        self._platform_url = self._version_url + '/' + self._platform + '/'

    @abc.abstractmethod
    def needed_lib_urls(self):
        raise NotImplementedError()


class TTSChannel(Channel):

    def __init__(self):
        super().__init__()

        self._channel = 'tts'
        self._channel_dir = BASE_DIR / '_tts'

    def needed_lib_urls(self):
        libs = {
            'win32': ''
        }


if __name__ == '__main__':
    c = TTSChannel()
    c.download()
