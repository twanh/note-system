import getpass
from typing import Optional
from typing import TypedDict

import keyring
import requests
from termcolor import colored

from notesystem.modes.base_mode import BaseMode


class UploadModeArguments(TypedDict):

    path: str
    url: str
    username: Optional[str]
    save_credentials: Optional[bool]


class UploadMode(BaseMode[UploadModeArguments]):

    def _run(self, args: UploadModeArguments) -> None:

        self.path = args['path']
        self.url = args['url']
        self.username = args['username']
        self.save_credentials = args['save_credentials']

        self._get_login()
        self._login()
        self._upload_notes()

    def _get_login(self) -> None:

        if self.username is not None:
            self.password = keyring.get_password('notesystem', self.username)
            if self.password is not None:
                return

        print(
            colored(
                'Please login using your notesystem server information.',
                'cyan',
                attrs=['bold'],
            ),
        )

        self.username = input('Username: ').strip()
        self.password = getpass.getpass('Password (input hidden): ')

        if self.save_credentials:
            keyring.set_password(
                'notesystem',
                self.username,
                self.password,
            )

    def _login(self) -> None:

        # Check that url ends with /
        if self.url.endswith('/'):
            login_url = f'{self.url}auth/login/api/'
        else:
            login_url = f'{self.url}/auth/login/api/'

        req = requests.post(
            login_url,
            json={
                'username': self.username,
                'password': self.password,
            },
        )
        if req.ok:
            req_json: dict[str, str] = req.json()
            ac_token = req_json.get('access_token', None)
            if ac_token is not None:
                self.access_token = ac_token
            else:
                # TODO: HANDLE ME
                raise NotImplementedError(req.content)

    def _upload_notes(self):
        print('Uploading')