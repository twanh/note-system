import os
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import TypedDict

from termcolor import colored

from notesystem.common.utils import find_all_md_files
from notesystem.common.visual import print_search_result
from notesystem.modes.base_mode import BaseMode


class SearchModeArguments(TypedDict):
    pattern: str
    path: str
    tag_str: Optional[str]
    topic: Optional[str]
    case_insensitive: Optional[bool]


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
        Raises:
            {FileNotFoundError} -- When the given path cannot be found
        """

        if 'tag_str' in args and args['tag_str'] is not None:
            self.tags = args['tag_str'].split(' ')
        else:
            self.tags = []
        self.topic = args['topic']
        self.case_insensitive = args['case_insensitive']
        self.pattern = args['pattern']
        self.path = args['path']
        self.matches: List[SearchMatch] = []

        if os.path.isfile(self.path):
            self._search_file(self.path)
        elif os.path.isdir(self.path):
            self._search_dir(self.path)
        else:
            raise FileNotFoundError(f'{self.path} could not be found')

        # Print out the results
        if self._visual:
            c = 0
            for match in self.matches:
                for _ in match['matched_lines']:
                    c += 1

            print(
                colored('Found', 'cyan'),
                colored(str(c), 'cyan', attrs=['bold']),
                colored('results: ', 'cyan'),
            )
            for match in self.matches:
                print_search_result(match, self.pattern)

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
            if self.case_insensitive:
                if self.pattern.lower() in line.lower():
                    line_match = LineMatch(line_nr=i, line=line)
                    matched_lines.append(line_match)
            else:
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

    def _search_dir(self, path: str) -> None:
        """Search (recursively) through all markdown files in a directory

        Finds all the markdown files in an directory and searches each
        one of them for the given pattern.

        Arguments:
            path {str} -- The path of the directory to search through
        Raises:
            {NotADirectoryErro} -- When the given path is not a dir.
        """
        # TODO: Add nice progress bar in visual mode

        if not os.path.isdir(os.path.abspath(path)):
            self._logger.error(
                f'Could not find directory: {os.path.abspath(path)}. \
                Please provide a valid directory.',
            )
            raise NotADirectoryError

        md_files = find_all_md_files(path)
        for file_path in md_files:
            self._search_file(file_path)
