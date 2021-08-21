import logging
import sys
from typing import Optional
from typing import Sequence

from notesystem.common.config import Config  # type: ignore
from notesystem.modes.base_mode import BaseMode
from notesystem.modes.base_mode import ModeOptions
from notesystem.modes.check_mode.check_mode import CheckMode
from notesystem.modes.convert_mode import ConvertMode
from notesystem.modes.convert_mode import PandocOptions
from notesystem.modes.search_mode import SearchMode
from notesystem.modes.upload_mode import UploadMode


def main(argv: Optional[Sequence[str]] = None):

    if argv is None:
        argv = sys.argv[1:]

    # Create logger
    logging.basicConfig(
        format='[%(levelname)s:%(name)s] @ %(asctime)s: %(message)s',
        datefmt='%H:%M:%S',
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)

    c = Config()
    config = c.parse(argv)

    # Set the general settings
    if config['general']['verbose']['value']:
        logging.getLogger().setLevel(logging.INFO)

    mode: Optional[BaseMode] = None
    options: Optional[ModeOptions] = None

    if 'check' in config:
        # start check mode
        mode = CheckMode()
        disabled_errors = []
        for disabled_error in config['check']['disabled_errors']:
            if disabled_error['value'] == True:
                disabled_errors.append(disabled_error['dest'][2:])
        options = {
            'visual': not config['general']['no_visual']['value'],
            'args': {
                'in_path': config['check']['in_path']['value'],
                'fix': config['check']['fix']['value'],
                'simple_errors': config['check']['simple_errors']['value'],
                'disabled_errors': disabled_errors,
            },

        }
    elif 'convert' in config:
        # start convert mode
        mode = ConvertMode()
        pandoc_options: PandocOptions = {
            'arguments': config['convert']['pandoc_args']['value'],
            'template': config['convert']['pandoc_template']['value'],
            'output_format': (
                'pdf'
                if config['convert']['to_pdf']['value']
                else 'html'
            ),
            'ignore_warnings': config['convert']['ignore_warnings']['value'],
        }
        options = {
            'visual': not config['general']['no_visual']['value'],
            'args': {
                'in_path': config['convert']['in_path']['value'],
                'out_path': config['convert']['out_path']['value'],
                'watch': config['convert']['watch']['value'],
                'pandoc_options': pandoc_options,
            },
        }

    elif 'search' in config:
        mode = SearchMode()
        search_args = {
            'pattern': config['search']['pattern']['value'],
            'path': config['search']['path']['value'],
            'tag_str': config['search']['tags']['value'],
            'tag_delimiter': config['search']['tag_delimiter']['value'],
            'topic': config['search']['topic']['value'],
            'case_insensitive': config['search']['case_insensitive']['value'],
            'title': config['search']['title']['value'],
            'full_path': config['search']['full_path']['value'],
        }

        options = {
            # TODO: Extract visual into variable
            'visual': not config['general']['no_visual']['value'],
            'args': search_args,
        }
    elif 'upload' in config:

        mode = UploadMode()
        upload_args = {
            'path': config['upload']['path']['value'],
            'url': config['upload']['url']['value'],
            'username': config['upload']['username']['value'],
            'save_credentials': config['upload']['save_credentials']['value'],
        }

        options = {
            'visual': not config['general']['no_visual']['value'],
            'args': upload_args,
        }

    else:
        raise SystemExit(1)

    mode.start(options)


if __name__ == '__main__':
    main()
