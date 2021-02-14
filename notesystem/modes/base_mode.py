"""Base class for modes"""
import abc
import logging
from typing import TypedDict, Dict

class ModeOptions(TypedDict):
    # The parsed command line argumens asocciated with the mode 
    # args: Dict[str, str]
    # Wether to the mode should display visual's (in the termial)
    # E.g: the convert mode prints the amount of files found, and displays a 
    # Progress bar if visual is true
    visual: bool
    args: Dict

class Mode(abc.ABC):
    """
    The Mode interface declares a method for running the mode.
    """
    @abc.abstractmethod
    def start(self, options: ModeOptions) -> None:
        """Define the method that should be run to use a mode"""

    def _run(self, args: Dict[str, str]):
        """Define the method that defines the mode's functionallity"""

class BaseMode(Mode):
    """
    Implements the default behaviour of a mode.
    """

    def __init__(self):
        # Initialize a logger for every mode
        self._logger = logging.getLogger(self.__class__.__name__)

    def start(self, options: ModeOptions) -> None:
        """Starts the mode

        Start stores wether the mode should run visual or not.
        Then it starts the mode using the (private) run method.

        Note: Every mode *has to* implement it's own `_run` method which handles
        the actual behaviour/functionallity of the mode.

        Arguments:
            options {ModeOptions} -- The options for the mode

        Returns:
            None
        """
        self._logger.debug(f"Starting mode with options: {options}")
        self._visual = options['visual']
        self._run(options['args'])

    def _run(self, args: Dict[str, str]):
        raise NotImplemented

