import abc
import os
import pathlib
import re
import shutil
import stat
import sys
from hashlib import md5

import openctp_ctp
import requests

CHANNELS = ('ctp', 'tts',)

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

        pkg_path = pathlib.Path(openctp_ctp.__file__)
        self._lib_path = pkg_path.parent.parent / 'openctp_ctp.libs'

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
        print('Downloading', name)
        rsp = requests.get(url)
        if 200 != rsp.status_code:
            raise Exception(f'Download {name} failed: {rsp.status_code} {rsp.text}')
        # check md5
        if md5_string != md5(rsp.content).hexdigest():
            raise Exception('md5 check failed')

        # save lib
        with open(file, 'wb') as f:
            f.write(rsp.content)

    def download_libs(self):
        rsp = requests.get(self._platform_url)
        if 200 != rsp.status_code:
            raise Exception(f'Parse libs failed: {rsp.status_code} {rsp.text}')

        text = rsp.text
        for line in text.split('\n'):
            if 'class="lib"' not in line:
                continue

            if self._platform.startswith('win'):
                ret = re.match(r'^.*>(.+\.dll)</a> +(\w+)$', line)
            elif self._platform.startswith('linux'):
                ret = re.match(r'^.*>(.+\.so)</a> +(\w+)$', line)
            elif self._platform.startswith('darwin'):
                # todo
                pass
            else:
                raise Exception(f'Unsupported platform: {self._platform}')

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

    def backup(self):
        lib_names = []
        for _, _, filenames in os.walk(self._tmp_dir):
            for filename in filenames:
                if not filename.startswith('thost') and not filename.startswith('libthost'):
                    continue
                lib_names.append(filename)

        if len(lib_names) == 2:
            print("Already backup", lib_names)
        else:
            for _, _, filenames in os.walk(self._lib_path):
                for filename in filenames:
                    if not filename.startswith('thost') and not filename.startswith('libthost'):
                        continue

                    lib_names.append(filename)
                    dst = self._tmp_dir / filename
                    shutil.move(self._lib_path / filename, dst)
            print("Backup", lib_names)

        return lib_names

    @abc.abstractmethod
    def switch(self):
        raise NotImplementedError()


class CTPChannel(Channel):
    def __init__(self):
        super().__init__()

        self._channel = 'CTP'
        # self._channel_dir = BASE_DIR / f'_{self._channel}'

    def switch(self):
        print(f'Switch to {self._channel} channel.')
        # for _, _, filenames in os.walk(self._lib_path):
        #     for filename in filenames:
        #         if not filename.startswith('thost'):
        #             continue
        #
        #         os.remove(self._lib_path / filename)

        for _, _, filenames in os.walk(self._tmp_dir):
            for filename in filenames:
                if not filename.startswith('thost') and not filename.startswith('libthost'):
                    continue

                src = self._tmp_dir / filename
                dst = self._lib_path / filename
                # os.chmod(dst, 0o755)
                # print(os.lstat(dst))
                if os.path.exists(dst):
                    os.remove(dst)
                shutil.copyfile(src, dst)


class TTSChannel(Channel):

    def __init__(self):
        super().__init__()

        self._channel = 'tts'
        self._channel_dir = BASE_DIR / f'_{self._channel}'

    def switch(self):
        print(f'Switch to {self._channel} channel.')

        lib_names = self.backup()

        lib_dict = {}
        for lib_name in lib_names:
            s1, s2 = lib_name.split('-')
            s3, s4 = s2.split('.')
            lib_dict[f'{s1}.{s4}'] = lib_name

        for _, _, filenames in os.walk(self._channel_dir):
            for filename in filenames:
                if not filename.startswith('thost') and not filename.startswith('libthost'):
                    continue

                dst = self._lib_path / lib_dict[filename]
                # os.chmod(dst, stat.S_IREAD | stat.S_IWUSR)
                if os.path.exists(dst):
                    os.remove(dst)
                shutil.copyfile(self._channel_dir / filename, dst)

        print('Switch over')


if __name__ == '__main__':
    c = TTSChannel()
    c.download()
    c.switch()
