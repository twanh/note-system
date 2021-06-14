import os
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import TypedDict

from notesystem.modes.base_mode import BaseMode


class SearchModeArguments(TypedDict):
    pattern: str
    path: str
    tag_str: Optional[str]


class LineMatch(NamedTuple):
    line_nr: int
    line: str


class SearchMatch(TypedDict):
    path: str
    tags: Optional[List[str]]  # The tags of the file
    title: Optional[str]
    topic: Optional[str]  # Also matched as subject
    # The line numbers of the matches (0 based)
    # Note: not optional because search match only used when a match is found
    matched_lines: List[LineMatch]


class SearchMode(BaseMode[SearchModeArguments]):
    """Search markdown files (notes) for the given search terms"""

    def _run(self, args) -> None:  # TODO: Should return exit code
        """Entry point for search mode

        Sets the state, and starts the search

        Arguments:
            args {SearchModeArguments} -- The arguments from the parser
        """

        self.tags = args['tag_str'].split(' ')
        self.pattern = args['pattern']
        self.path = args['path']
        self.matches: List[SearchMatch] = []

        if os.path.isfile(self.path):
            self._search_file(self.path)

    def _parse_frontmatter(self, file_lines: List[str]) -> Dict[str, str]:

        fm_data: Dict[str, str] = {}

        if not file_lines[0].startswith('---'):
            return fm_data

        for line in file_lines[1:]:
            if line.startswith('---'):
                break
            key, value = line.strip().split(':')
            fm_data[key.strip().lower()] = value.strip()

        return fm_data

    def _search_file(self, file_path: str) -> None:
        """Search through the given file and adds matches to the matches list

        Search for the pattern in given file (file_path) if tags are given
        that need to be matched they are checked first to prevent looking
        throught the whole file.

        If an match is found a SearchMatch (dict) is added to the matches list.

        Arguments:
            file_path {str} -- The path of the file to search through
        """

        title = None
        topic = None
        tags = None

        with open(file_path, 'r') as file:
            lines = file.readlines()

        if not len(lines) >= 1:
            return  # Emtpy file

        # Check if there is front matter
        if lines[0].startswith('---'):
            fm = self._parse_frontmatter(lines)
            if len(self.tags) >= 1:
                if 'tags' in fm:
                    # TODO: create tag delimiter option
                    tags = fm['tags'].split(' ')
                    matched_tags = [tag for tag in self.tags if tag in tags]
                    if len(matched_tags) < 1:
                        return  # The tags do not match
                else:
                    return  # No tags in the file but tags are searched for
            if 'title' in fm:
                title = fm['title']

            if 'topic' in fm:
                topic = fm['topic']
            elif 'subject' in fm:
                topic = fm['subject']

        # Loop over the file to search for the given pattern
        # TODO: Allow for regex patterns (turn on with --regex flag)
        matched_lines: List[LineMatch] = []
        for i, line in enumerate(lines):
            # TODO: Allow for case insensitive search
            if self.pattern in line:
                line_match = LineMatch(line_nr=i, line=line)
                matched_lines.append(line_match)

        if len(matched_lines) < 1:
            return  # No matches

        final_match = SearchMatch(
            path=file_path,
            matched_lines=matched_lines,
            tags=tags,
            title=title,
            topic=topic,
        )

        self.matches.append(final_match)
