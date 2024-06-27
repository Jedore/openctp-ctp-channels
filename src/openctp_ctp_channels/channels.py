import abc
import os
import re
import shutil
import sys
import sysconfig
from hashlib import md5
from pathlib import Path

import requests

CHANNELS = ('ctp', 'tts',)

BASE_DIR = Path(__file__).parent


class Channel(abc.ABC):

    def __init__(self):
        self._channel = ''
        self._base_url = 'https://ctp-channels.jedore.top'
        self._channel_url = ''
        self._version_url = ''
        self._platform_url = ''

        self._channel_dir = Path()
        self._ctp_dir = BASE_DIR / '_ctp'
        self.check_ctp_dir()

        self._openctp_version = self._get_openctp_ctp_version()
        self._ctp_version = '.'.join(self._openctp_version.split('.')[:3])
        self._platform = self._get_platform()
        self._ctp_lib_path = self._get_openctp_ctp_lib_path()

    @property
    def channel(self):
        return self._channel

    @staticmethod
    def _get_openctp_ctp_version():
        for line in os.popen('pip show openctp-ctp').read().splitlines():
            if 'Version' in line:
                return line.split()[-1].strip()

    @staticmethod
    def _get_openctp_ctp_lib_path():
        # todo if openctp_ctp.lib not exists, raise Exception, darwin
        return Path(sysconfig.get_path('purelib')) / 'openctp_ctp.libs'

    @staticmethod
    def _get_platform():
        if sys.platform.startswith('win32'):
            if sys.maxsize == 0x7FFFFFFF:
                # 32bit
                platform = "win32"

            elif sys.maxsize == 0x7FFFFFFFFFFFFFFF:
                # 64bit
                platform = "win64"
            else:
                raise Exception("Unsupported windows arch!")

        elif sys.platform.startswith('linux'):
            platform = 'linux64'
        else:
            raise Exception("Unsupported platform:", sys.platform)

        return platform

    @staticmethod
    def _check_lib_prefix(libname):
        if not libname.startswith('thost') and not libname.startswith('libthost'):
            return True
        return False

    def check_ctp_dir(self):
        if not self._ctp_dir.exists():
            self._ctp_dir.mkdir(exist_ok=True)

    def _check_channel_dir(self):
        if not self._channel_dir.exists():
            self._channel_dir.mkdir(exist_ok=True)

    def download_lib(self, name: str, md5_string: str):
        file = self._channel_dir / name
        if file.exists():
            # print('Already downloaded:', name)
            return

        url = self._platform_url + name
        # print('Downloading', name)
        rsp = requests.get(url)
        if 200 != rsp.status_code:
            raise Exception(f'Download {name} failed: {rsp.status_code} {rsp.text}')

        # check md5
        if md5_string != md5(rsp.content).hexdigest():
            raise Exception('md5 check failed')

        # save lib
        with open(file, 'wb') as f:
            f.write(rsp.content)

    def _download_libs(self):
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
                # todo download darwin libs
                pass
            else:
                raise Exception(f'Unsupported platform: {self._platform}')

            name = ret.group(1)
            md5_string = ret.group(2)
            self.download_lib(name, md5_string)

    def download(self):
        self._generate_url()
        self._check_channel_dir()
        self._download_libs()

    def _generate_url(self):
        self._channel_url = self._base_url + '/' + self._channel
        self._version_url = self._channel_url + '/' + self._ctp_version
        self._platform_url = self._version_url + '/' + self._platform + '/'

    def _backup(self):
        lib_names = []
        for _, _, filenames in os.walk(self._ctp_dir):
            for filename in filenames:
                if self._check_lib_prefix(filename):
                    continue
                lib_names.append(filename)

        if len(lib_names) == 2:
            # print("Already backup", lib_names)
            pass
        else:
            lib_names.clear()
            for _, _, filenames in os.walk(self._ctp_lib_path):
                for filename in filenames:
                    if self._check_lib_prefix(filename):
                        continue

                    lib_names.append(filename)
                    dst = self._ctp_dir / filename
                    shutil.copyfile(self._ctp_lib_path / filename, dst)
            # print("Backup", lib_names)

        return lib_names

    def _get_libs(self):
        lib_names = set()
        for _, _, filenames in os.walk(self._ctp_dir):
            for filename in filenames:
                if self._check_lib_prefix(filename):
                    continue
                lib_names.add(filename)

        for _, _, filenames in os.walk(self._ctp_lib_path):
            for filename in filenames:
                if self._check_lib_prefix(filename):
                    continue
                lib_names.add(filename)

        return tuple(lib_names)

    @abc.abstractmethod
    def switch(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _copy_libs(self):
        raise NotImplementedError()

    def current_channel(self):
        current_md5 = set()
        channel = 'ctp'
        for file in os.listdir(self._ctp_lib_path):
            if self._check_lib_prefix(file):
                continue
            with open(self._ctp_lib_path / file, 'rb') as f:
                current_md5.add(md5(f.read()).hexdigest())

        for dir_path, dir_names, filenames in os.walk(BASE_DIR):
            tmp_md5 = set()
            if not dir_names and filenames:
                for filename in filenames:
                    if self._check_lib_prefix(filename):
                        continue
                    with open(os.path.join(dir_path, filename), 'rb') as f:
                        tmp_md5.add(md5(f.read()).hexdigest())
                if tmp_md5 == current_md5:
                    channel = os.path.basename(dir_path)[1:]
                    break

        return channel


class CTPChannel(Channel):
    def __init__(self):
        super().__init__()

        self._channel = 'ctp'
        self._channel_dir = BASE_DIR / f'_{self._channel}'

    def _copy_libs(self):
        for _, _, filenames in os.walk(self._channel_dir):
            for filename in filenames:
                if self._check_lib_prefix(filename):
                    continue

                src = self._channel_dir / filename
                dst = self._ctp_lib_path / filename

                if self._platform.startswith('linux'):
                    if os.path.exists(dst):
                        os.remove(dst)

                shutil.copyfile(src, dst)

    def switch(self):
        if self.current_channel() == self._channel:
            print('Current channel is', self._channel)
            return

        print(f'Switch to {self._channel} channel.')
        self._copy_libs()


class TTSChannel(Channel):

    def __init__(self):
        super().__init__()

        self._channel = 'tts'
        self._channel_dir = BASE_DIR / f'_{self._channel}'

    def _copy_libs(self):
        lib_dict = {}
        for lib_name in self._get_libs():
            s1, s2 = lib_name.split('-')
            s3, s4 = s2.split('.')
            lib_dict[f'{s1}.{s4}'] = lib_name

        for _, _, filenames in os.walk(self._channel_dir):
            for filename in filenames:
                if self._check_lib_prefix(filename):
                    continue

                dst = self._ctp_lib_path / lib_dict[filename]

                if self._platform.startswith('linux'):
                    if os.path.exists(dst):
                        os.remove(dst)

                shutil.copyfile(self._channel_dir / filename, dst)

    def switch(self):
        if self.current_channel() == self._channel:
            print('Current channel is', self._channel)
            return

        print(f'Switch to {self._channel} channel.')

        self._backup()
        self._copy_libs()


if __name__ == '__main__':
    c = TTSChannel()
    c.download()
    c.switch()
