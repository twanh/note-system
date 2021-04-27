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
            'visual': config['general']['visual']['value'],
            'args': {
                'in_path': config['check']['in_path']['value'],
                'fix': config['check']['fix']['value'],
                'disabled_errors': disabled_errors,
            },

        }
    elif 'convert' in config:
        # start convert mode
        mode = ConvertMode()
        pandoc_options: PandocOptions = {
            'arguments': config['convert']['pandoc_args']['value'],
            'template': config['convert']['pandoc_template']['value'],
            'output_format': 'html' if config['convert']['to_pdf'] else 'pdf',
            'ignore_warnings': config['convert']['ignore_warnings']['value'],
        }
        options = {
            'visual': config['general']['visual']['value'],
            'args': {
                'in_path': config['convert']['in_path']['value'],
                'out_path': config['convert']['out_path']['value'],
                'watch': config['convert']['watch']['value'],
                'pandoc_options': pandoc_options,
            },
        }
    else:
        raise SystemExit(1)

    mode.start(options)


if __name__ == '__main__':
    main()
