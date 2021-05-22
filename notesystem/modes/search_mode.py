from typing import Optional
from typing import TypedDict

from notesystem.modes.base_mode import BaseMode


class SearchModeArguments(TypedDict):
    pattern: str
    path: str
    tag_str: Optional[str]


class SearchMode(BaseMode[SearchModeArguments]):

    def _run(self, args):
        self._logger.info('Search mode')
