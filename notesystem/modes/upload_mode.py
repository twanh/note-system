import getpass
import hashlib
import os
import shutil
import tempfile
import time
from typing import Dict
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
        self._api_login()
        self._api_upload_notes()

    def _get_login(self) -> None:
        """
        Displays a nice prompt to the user asking for
        username and password and saves the credentials if nessesary
        """

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

    def _api_login(self) -> None:
        """Perform the login request"""

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
            req_json: Dict[str, str] = req.json()
            ac_token = req_json.get('access_token', None)
            if ac_token is not None:
                self.access_token = ac_token
                # TODO: Extract the printing of status etc to __init__
                print(
                    colored('Logged in!', 'green', attrs=['bold']),
                )
                return

        # 400 BAD REQUEST
        r_json: Dict[str, str] = req.json()
        if req.status_code == 400:
            msg: Optional[str] = r_json.get('msg', None)
            if msg:
                print(
                    colored(msg, 'red', attrs=['bold']),
                )

            # Should perhaps raise execption that should be caught??
            raise SystemExit(1)

        else:
            raise AssertionError(
                'Got an unkown response from the server',
                r_json,
            )

    def _api_upload_notes(self):
        """Upload the notes to the server using the api"""

        if self.url.endswith('/'):
            url = f'{self.url}upload/zip/?api=true'
        else:
            url = f'{self.url}/upload/zip/?api=true'

        # ZIP the notes
        with tempfile.TemporaryDirectory() as tmpdir:
            # TODO: Use better filename
            file_path = os.path.join(tmpdir, f'{time.time_ns()}')
            print(colored(f'Creating ZIP archive of {self.path}', 'cyan'))

            shutil.make_archive(
                file_path,
                'zip',
                self.path,
            )

            file_path = file_path + '.zip'
            # Create the checksum
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as file:
                for block in iter(lambda: file.read(4096), b''):
                    sha256.update(block)

            sha_hash = sha256.hexdigest()

            # Upload the notes
            req = requests.post(
                url,
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                },
                data={'checksum': sha_hash},
                files={'zip': open(file_path, 'rb')},
            )
            if req.status_code == 200:
                print(
                    colored('Uploaded the notes!', 'green', attrs=['bold']),
                )

            else:
                print(
                    colored(
                        'An error occured while uploading, please try again!',
                        'red',
                        attrs=['bold'],
                    ),
                )
