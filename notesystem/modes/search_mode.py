from typing import TypedDict

from notesystem.modes.base_mode import BaseMode


class SearchModeArguments(TypedDict):
    query: str


class SearchMode(BaseMode[SearchModeArguments]):

    def _run(self, args):
        self._logger.info('Search mode')
        print('In search mode', args)
