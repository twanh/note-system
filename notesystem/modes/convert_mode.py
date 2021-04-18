"""
Mode responsible for converting markdown files
(and directories with markdown files) to html files
"""
import os
import shutil
import subprocess
import time
from typing import cast
from typing import Optional
from typing import TypedDict

import tqdm
from termcolor import colored
from watchdog.events import FileMovedEvent
from watchdog.events import FileSystemEvent
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver as Observer
from yaspin import yaspin
from yaspin.spinners import Spinners

from notesystem.common.utils import find_all_md_files
from notesystem.modes.base_mode import BaseMode


class PandocOptions(TypedDict):
    # Command line arguments to be passed to pandoc
    arguments: Optional[str]
    # The template to be used
    template: Optional[str]
    # The output format (for now 'html' or 'pdf')
    output_format: str
    # Wether to ignore warnings thrown by pandoc
    ignore_warnings: bool


class ConvertModeArguments(TypedDict):
    # The input path
    in_path: str
    # The output path
    out_path: str
    # Wether watch mode is enabled
    watch: bool
    # The string of arguments needed to be passed trough to pandoc
    pandoc_options: PandocOptions


class ConvertMode(BaseMode[ConvertModeArguments]):
    """Convert markdown files to html"""

    def _run(self, args: ConvertModeArguments) -> None:
        """Internal entry point for ConvertMode

        Check if the inpath is actually a file or folder and starts the
        correct convertion process.

        Arguments:
            args {ConvertModeArguments} -- The arguments from the parser

        """

        # Check if pandoc is installed
        pandoc_cmd = shutil.which('pandoc')
        if pandoc_cmd is None:
            self._logger.error(
                'Could not find pandoc. Make sure it is in your path.',
            )
            raise SystemExit()
        self._logger.debug(f'Found pandoc @ {pandoc_cmd}')

        # Set pandoc options
        self._pandoc_options: PandocOptions = args['pandoc_options']

        # Make sure this variable exists
        # by default is is False but it gets set correctly in _convert_dir
        self._converting_dir = False

        # Check if args[in_path] is a file or a directory
        if os.path.isdir(os.path.abspath(args['in_path'])):
            self._convert_dir(args['in_path'], args['out_path'])
        elif os.path.isfile(os.path.abspath(args['in_path'])):
            if self._visual:
                print(
                    colored(
                        f"Converting {args['in_path']} -> {args['out_path']}",
                        'green',
                    ),
                )
            self._convert_file(
                args['in_path'], args['out_path'],
            )
        else:
            raise FileNotFoundError

        # Watch mode is started after the file (folder) is converted.
        #
        if args['watch']:
            # Start watcher
            self._start_watch_mode(args)

    def _create_watch_handler(
        self,
        in_path: str,
        out_path: str,
    ) -> FileSystemEventHandler:
        """Create the handler for the filewatcher

        Arguments:
            in_path {str}  -- The input path (file or folder).
            out_path {str} -- The path the output should be written to.

        Returns:
            {FileSystemEventHandler} -- The handler that converts created
                                        and modified files

        """

        # Create s special convert function with access to the CheckMode scope.
        def conv(file_path: str):
            if self._visual:
                # Extra print, otherwise text will show up after the spinner
                print()
                print(
                    colored(
                        'Converting:', 'blue', attrs=[
                            'bold',
                        ],
                    ), colored(f'{file_path}', 'blue'),
                )

            # Create nessesary subdirectories if in_path is an directory
            # TODO: Create helper function (DRY)
            #       Perhaps a DS, {in_path: out_path}? or [(in_path, out_path)]
            if os.path.isdir(os.path.abspath(in_path)):
                file_path = os.path.abspath(file_path)
                dir_path = file_path[len(os.path.abspath(in_path)):]
                sub_dirs = dir_path.split('/')[1:-1]
                cur_path = os.path.abspath(out_path)
                for d in sub_dirs:
                    cur_path = os.path.join(cur_path, d)
                    print(os.path.isdir(cur_path))
                    print(cur_path)
                    print(os.path.exists(cur_path))
                    if not os.path.isdir(cur_path):
                        self._logger.info(
                            f'Making new (sub)directory {cur_path}',
                        )
                        try:
                            os.mkdir(cur_path)
                        except FileNotFoundError:
                            self._logger.warning(
                                f'Could not create (sub)directory {cur_path}',
                            )
                        except Exception as e:
                            self._logger.error(e)

                in_filename = file_path.split('/')[-1]
                out_filename = in_filename.replace('.md', '.html')
                out_file_path = os.path.join(cur_path, out_filename)

                self._convert_file(file_path, out_file_path)
                self._logger.info(f'Converted {in_filename} -> {out_filename}')

            else:
                # Convert the file if the in_path is a file
                self._convert_file(file_path, out_path)
                self._logger.info(f'Converted {file_path} -> {out_path}')

        # The special handler to handle modified and created events
        class Handler(FileSystemEventHandler):

            def on_any_event(self, event: FileSystemEvent):
                if event.is_directory:
                    # TODO: Handle, directory renames, deletes, etc...
                    return None
                elif (
                    event.event_type == 'created' or
                    event.event_type == 'modified'
                ):
                    # Only convert markdown files
                    if event.src_path.endswith('.md'):
                        conv(os.path.abspath(event.src_path))
                # Remove deleted files from the output dir
                elif event.event_type == 'deleted':

                    # Extra check that the file does not exist
                    if os.path.exists(event.src_path):
                        # Should error?
                        return None

                    # The inpath is a file so we can just delete the outpath
                    if os.path.isfile(in_path):
                        os.remove(out_path)

                    dirs_path = os.path.abspath(event.src_path)[
                        len(
                            os.path.abspath(in_path),
                        ) + 1:
                    ].replace('.md', '.html')
                    delete_path = os.path.join(
                        os.path.abspath(out_path), dirs_path,
                    )

                    # Delete the file
                    try:
                        print('\n')
                        print(
                            colored(
                                f'Deleting: {delete_path}',
                                'red',
                            ),
                        )
                        os.remove(delete_path)
                    except OSError:
                        print(
                            colored(
                                f'[ERROR]: Could not delete {delete_path}',
                                'red',
                                attrs=['bold'],
                            ),
                        )

                # Move the moved file in the output directory
                elif event.event_type == 'moved':
                    # TODO:
                    # - Make sure the output directory exists
                    # - Add retry logic, for failing moves

                    moved_event = cast(FileMovedEvent, event)
                    # Get the starting file
                    start_file_path = moved_event.src_path
                    start_dirs_path = os.path.abspath(start_file_path)[
                        len(
                            os.path.abspath(in_path),
                        ) + 1:
                    ].replace('.md', '.html')
                    start_output_file_path = os.path.join(
                        os.path.abspath(out_path), start_dirs_path,
                    )
                    # Get the new filename
                    end_file_path = moved_event.dest_path
                    end_dirs_path = os.path.abspath(end_file_path)[
                        len(
                            os.path.abspath(in_path),
                        ) + 1:
                    ].replace('.md', '.html')
                    end_output_file_path = os.path.join(
                        os.path.abspath(out_path), end_dirs_path,
                    )
                    try:
                        print('\n')
                        print(
                            colored(
                                f'Moving {start_output_file_path} -> {end_output_file_path}',  # noqa: E501
                                'red',
                            ),
                        )
                        os.rename(start_output_file_path, end_output_file_path)
                    except OSError as e:
                        print(
                            colored(
                                '[ERROR]: Could not move the files.',
                                'red',
                                attrs=['bold'],
                            ),
                        )
                        print(
                            colored(
                                str(e),
                                'red',
                                attrs=['bold'],
                            ),
                        )

        return Handler()

    def _start_watch_mode(self, args: ConvertModeArguments) -> None:
        """Starts and runs the watch mode until canceled

        Arguments:
            args {ConvertModeArguments} -- The arguments for convert mode

        """

        # Use custom event handler
        event_handler = self._create_watch_handler(
            args['in_path'], args['out_path'],
        )

        # Init the observer
        observer = Observer()
        observer.schedule(event_handler, args['in_path'], recursive=True)

        self._logger.debug(f"Starting watch mode for: {args['in_path']}")

        if self._visual:
            print(
                colored('Starting watcher for:', 'blue', attrs=['bold']),
                colored(f"{os.path.abspath(args['in_path'])}", 'blue'),
            )
        else:
            self._logger.info(f"Starting watch mode for: {args['in_path']}")

        # Start
        observer.start()
        # Keep the process running while
        # the watcher watches (until KeyboardInterrupt)
        try:
            while True:
                # Pretty spinner =)
                spinner_text = colored(
                    'Watching files', 'blue',
                ) + colored(' (use Ctrl+c to exit)', 'red')
                with yaspin(
                    Spinners.bouncingBar,
                    text=spinner_text,
                    color='blue',
                ):
                    time.sleep(1)
        except KeyboardInterrupt:
            self._logger.debug('Got a KeyboardInterrupt, stopping watcher.')
            observer.stop()
        observer.join()

        self._logger.debug(f"Stoped watching {args['in_path']}")
        if self._visual:
            print(
                colored('Stoped watcher for:', 'blue', attrs=['bold']),
                colored(f"{os.path.abspath(args['in_path'])}", 'blue'),
            )
        else:
            self._logger.info(f"Stoped watching {args['in_path']}")

    def _convert_file(self, in_file: str, out_file: str) -> None:
        """Convert a markdown file to html

        Using pandoc the in_file is converted to a html file which is saved at
        the out_file path. By default mathjax is enabled and GitHub.html5
        template is used

        If the `out_file` already exists it is overwritten.
        NOTE: This is also default pandoc behaviour

        Arguments:
            in_file {str}  -- The absolute path to the file that needs
                              to be converted
            out_file {str} -- The absolute path to where the convted
                              file should be saved

        Returns:
            {None}
        """

        # Create the pandoc command
        arguments = ''  # No arguments by default
        if self._pandoc_options['arguments'] is not None:
            # Check for arguments that should not be passed to pandoc
            not_allowed_args = [
                '-o', '--to',
                '--from', '--template', '--mathjax',
            ]

            for not_allowed in not_allowed_args:
                if not_allowed in self._pandoc_options['arguments']:
                    self._logger.error(
                        f'{not_allowed} is allowed as an (extra) pandoc \
                        argument.',
                    )
                    raise SystemExit(1)

            arguments = self._pandoc_options['arguments']

        output_format = self._pandoc_options['output_format']
        if output_format == 'pdf':

            template = None  # No template by default
            template_str = ''  # no template by default

            if self._pandoc_options['template'] is not None:
                template = self._pandoc_options['template']
                template_str = f'--template {template}'

            if not out_file.endswith('.pdf'):
                out_file_correct = '.'.join(out_file.split('.')[:-1]) + '.pdf'
            else:
                out_file_correct = out_file

            pd_command = f'pandoc {in_file} -o {out_file_correct} {template_str} --mathjax {arguments} -t pdf'  # noqa: E501

        else:
            # Default/fallback to html
            template = 'GitHub.html5'  # Default template (for html)
            template_str = f'--template {template}'
            if self._pandoc_options['template'] is not None:
                if self._pandoc_options['template'] == '':
                    template_str = ''
                else:
                    template = self._pandoc_options['template']
                    template_str = f'--template {template}'

            pd_command = f'pandoc {in_file} -o {out_file} {template_str} --mathjax {arguments} -t html'  # noqa: E501

        self._logger.info(f'Attempting convertion with command: {pd_command}')

        try:
            # Stdout and stderr are supressed so
            # that custom information can be shown
            result = subprocess.run(
                pd_command,
                shell=True,
                capture_output=True,
            )

            if result.stderr:
                error_text = result.stderr.decode('utf-8').strip()
                if self._visual:

                    # Helper function to print using tqdm write when
                    # converting a dir so that it does not
                    # mess up the progres bar
                    def print_correct(x):
                        if self._converting_dir:
                            return tqdm.tqdm.write(x)
                        else:
                            print(x)

                    if error_text.startswith('[WARNING]'):
                        if not self._pandoc_options['ignore_warnings']:
                            print_correct(
                                colored(
                                    'PANDOC WARNING:',
                                    'yellow', attrs=['bold'],
                                ),
                            )
                            print_correct(
                                colored(
                                    result.stderr.decode(
                                        'utf-8',
                                    ).strip(), 'yellow',
                                ),
                            )
                    else:
                        print_correct(
                            colored(
                                f'Could not convert {in_file} into {out_file}. See error message below.',  # noqa: E501
                                'red',
                                attrs=['bold'],
                            ),
                        )
                        print_correct(
                            colored(
                                'PANDOC ERROR:',
                                'red', attrs=['bold'],
                            ),
                        )
                        print_correct(
                            colored(
                                result.stderr.decode('utf-8').strip(),
                                'red',
                            ),
                        )
                    self._logger.debug(
                        f'Pandoc error (was printend on screen): {error_text}',
                    )
                else:
                    self._logger.warning(f'Pandoc error: {error_text}')

        except subprocess.CalledProcessError as se:
            self._logger.error(f'Could not convert {in_file} into {out_file}')
            self._logger.debug(se)
            raise SystemExit(1)

    def _convert_dir(self, in_dir_path: str, out_dir_path: str) -> None:
        """Converts all the markdown files in a directory (and subdirectory) to html

        Using pandoc all the files in the `in_dir_path` directory
        (and it's subdirectories) are converted to html and saved
        in the out_dir_path and if nessesary in their correct subfolder.

        So the folder structure and filenames stay the same.

        If the out_dir_path does not exits, it gets created
        and so do the subdirectories.

        Arguments:
            in_dir_path {str}  -- The directory where all the files that need
                                  to be converted are located
            out_dir_path {str} -- The directory where all the converted files
                                  will be saved.

        Returns:
            None

        """

        # Keep state wether a directory is being conveted
        # Other methods may need to change the way they handle things
        # or print (because of the progress bar)
        self._converting_dir = True

        if self._visual:
            print(
                colored(
                    f'Searching for files to convert in {in_dir_path}',
                    'green',
                ),
            )

        all_files = find_all_md_files(in_dir_path)
        self._logger.debug(f'Found {len(all_files) in {in_dir_path}}')
        self._logger.debug(all_files)

        if self._visual:
            print(
                colored('Found ', 'green') + colored(
                    str(len(all_files)),
                    'green', attrs=['bold'],
                ) + colored(' to convert!', 'green'),
            )

        # If in visual mode, a tqdm progress bar will be shown
        # If not in visual mode it will not be shown so tqdm is replaced with
        # a 'fake' tqdm function

        # The functions simple returns the first argument it
        # gets, which is the iterable
        fake_tqdm = lambda x, *args, **kwargs: x  # noqa: E731
        v_tqdm = tqdm.tqdm if self._visual else fake_tqdm

        # The default logger messes up the tqdm progress bar
        # if visual mode is enabled
        # Verbose and visual mode can be enabled at the same time,
        # so the logger temporarily
        # needs to use tqdm.write
        # FIXME: Actually make it work...
        # class TqdmLogger(logging.Handler):

        #     def __init__(self, level=logging.NOTSET):
        #         super().__init__(level)

        #     def emit(self, record):
        #         try:
        #             msg = self.format(record).strip()
        #             tqdm.tqdm.write(msg)
        #             self.close()
        #         except (KeyboardInterrupt, SystemExit):
        #             raise
        #         finally:
        #             msg = self.format(record).strip()
        #             tqdm.tqdm.write(msg)
        #             self.close()

        # Enable the tqdm logger
        # FIXME: TqdmLogger not working correctly
        # if self._visual:
        #     self._logger.addHandler(TqdmLogger())

        # The (root) out directory needs to be created if it does not exist yet
        if not os.path.exists(os.path.abspath(out_dir_path)):
            self._logger.info(f'Making new directory: {out_dir_path}')
            os.mkdir(out_dir_path)

        for file_path in v_tqdm(
            all_files,
            desc='Converting',
            ascii=True,
            colour='green',
        ):

            # Get the path of the subdirectory (if anny)
            # This is done so that the folder structure can
            # be copied over to the output
            # Get everything from the filepath after the in_dir_path
            dir_path = file_path[len(os.path.abspath(in_dir_path)):]
            # TODO: Adapt for windows
            # Split by / so there is an array of all the sub directories
            sub_dirs = dir_path.split('/')[1:-1]
            # Create the subdirectories needed for
            # the current file (if needed)
            # TODO: Could be (slightly) optimized by checking on
            # forehand if the final directory exists
            cur_path = out_dir_path
            for d in sub_dirs:
                # Add the subdirectory path to the
                # current path on each iteration
                cur_path = os.path.join(cur_path, d)
                if not os.path.isdir(cur_path):
                    self._logger.info(f'Making new (sub)directory: {cur_path}')
                    try:
                        os.mkdir(cur_path)
                    except FileNotFoundError:
                        self._logger.warning(
                            f'Could not create (sub)directory {cur_path}',
                        )
                    except Exception as e:
                        self._logger.error(e)

            # Convert the actual file
            in_filename = file_path.split('/')[-1]
            out_filename = in_filename.replace('.md', '.html')
            out_file_path = os.path.join(cur_path, out_filename)

            self._logger.info(f'Converted {in_filename} -> {out_filename}')
            self._convert_file(file_path, out_file_path)

        # Cleanup
        self._converting_dir = False

        # Remove the TqdmLogger after the progress bare is done
        # if self._visual:
        #     self._logger.removeHandler(TqdmLogger())
