import os
from unittest.mock import Mock
from unittest.mock import patch

import py
import pytest

from notesystem.modes.base_mode import ModeOptions
from notesystem.modes.search_mode import SearchMode
from notesystem.notesystem import main


@patch('notesystem.modes.search_mode.SearchMode._run')
def test_search_mode_called(run_mock: Mock):
    main(['search', 'pattern', 'location'])
    run_mock.assert_called_once()


@patch('notesystem.modes.search_mode.SearchMode.start')
def test_search_mode_called_with_correct_args_tags(start_mock: Mock):

    tag_str = 'hi'
    main(['search', 'pattern', 'location', '--tags', tag_str])

    expected_args = {
        'pattern': 'pattern',
        'path': 'location',
        'tag_str': tag_str,
        'topic': None,
        'case_insensitive': False,
        'title': None,
    }

    expected_options: ModeOptions = {
        'visual': True,
        'args': expected_args,
    }

    start_mock.assert_called_with(expected_options)


def test_split_tag_str_correctly():

    search_mode = SearchMode()
    tags = ['t1', 't2', 't3', 'ajj']
    args = {
        'pattern': 'pattern',
        'path': 'location',
        'tag_str': ' '.join(tags),
        'topic': None,
        'case_insensitive': False,
        'title': None,
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    try:
        search_mode.start(options)
    # It will throw FileNotFoundError because location does not exist
    # but that does not matter for this test
    except FileNotFoundError:
        pass

    assert search_mode.tags == tags


def test_split_tags_with_custom_delimiter_correctly():
    """This tests that the tag_str is sepereted correctly"""
    tags = ['t', 't2', 't4']
    search_mode = SearchMode()
    args = {
        'pattern': 'pattern',
        'path': 'location',
        'tag_str': ','.join(tags),
        'tag_delimiter': ',',
        'topic': None,
        'case_insensitive': False,
        'title': None,
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }

    try:
        search_mode.start(options)
    except FileNotFoundError:
        pass
    assert search_mode.tags == tags


def test_split_tags_in_note_with_custom_delimiter_correctly(
        tmpdir: py.path.local,
):

    file = tmpdir.join('testfile.md')
    file.write("""---
                  tags: t1,t2,t3,t4
                  ---
                  # Heading 1
                  <search_term>
               """)

    main([
        'search', '<search_term>', file.strpath,
        '--tags="t1"', '--tag-delimiter=","',
    ])


def test_allow_no_tag():

    search_mode = SearchMode()
    args = {
        'pattern': 'pattern',
        'path': 'location',
        'tag_str': None,
        'topic': None,
        'case_insensitive': False,
        'title': None,
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    try:
        search_mode.start(options)
    # It will throw FileNotFoundError because location does not exist
    # but that does not matter for this test
    except FileNotFoundError:
        pass

    assert search_mode.tags == []


@patch('notesystem.modes.search_mode.SearchMode._search_dir')
def test_search_dir_is_called_when_dir_is_given(mock: Mock):

    main(['search', 'pattern', os.getcwd()])

    mock.assert_called_once_with(os.getcwd())


@patch('notesystem.modes.search_mode.SearchMode._search_file')
def test_search_file_is_called_when_file_is_given(mock: Mock):

    main(['search', 'pattern', __file__])

    mock.assert_called_once_with(__file__)


# Testing the front matter parser
def test_parse_front_matter_handles_no_fm():

    # 'file' lines without front matter
    lines = ['These\n', 'are\n', '---\n', 'some\n', 'lines\n']

    search_mode = SearchMode()
    res = search_mode._parse_frontmatter(lines)

    assert res == {}
    assert len(res) == 0


@pytest.mark.parametrize(
    'lines, result',
    [
        (['---\n', 'title: Test title\n', '---\n'], {'title': 'Test title'}),
        (['---\n', 'tags: tag test\n', '---\n'], {'tags': 'tag test'}),
        (['---\n', 'subject: test\n', '---\n'], {'subject': 'test'}),
        (['---\n', 'topic: test\n', '---\n'], {'topic': 'test'}),
        (['---\n', 'other: test\n', '---\n'], {'other': 'test'}),
        (['---\n', 'date: 06-06-12\n', '---\n'], {'date': '06-06-12'}),
        (
            ['---\n', 'subject: test\n', 'title: test\n', '---\n'],
            {'subject': 'test', 'title': 'test'},
        ),
    ],
)
def test_parse_front_matter_parses_correct_data(lines, result):

    search_mode = SearchMode()
    res = search_mode._parse_frontmatter(lines)
    assert res == result


def test_parse_front_matter_handles_no_ending_dashses():
    """If the front matter is not ended correctly (`---`)"""

    lines = [
        '---\n', 'actual: fm\n', '# Heading 1\n',
        'paragraph 1\n', '## Heading 2\n',
    ]

    search_mode = SearchMode()
    res = search_mode._parse_frontmatter(lines)
    assert res == {'actual': 'fm'}


# Search funtionallity

# Pattern is found in file
@pytest.mark.parametrize(
    'file_contents,pattern,n_matches',
    [
        (
            """
    # Heading 1
    This is paragraph under heading 1 and this WORD should be found
    but this word should not be found.
    """, 'WORD', 1,
        ),
        (
            """
    # Heading 1
    This is paragraph under heading 1 and this WORD should be found
    but this word should not be found.
    """, 'thisisnotinthetext', 0,
        ),
        (
            """
    # Heading 1
    This is paragraph under heading 1 and this WORD should be found
    but this word should not be found.
    """, '1', 2,
        ),
        (
            """
    # Heading 1
    This is paragraph under heading 1 and this WORD should be found
    but this word should not be found.
    ## Heading 2
    Paragrpah 2
    """, '#', 2,
        ),
        (
            """
    # Heading 1
    This is paragraph under heading 1 and this WORD should be found
    but this word should not be found.
    ## Heading 2
    Paragrpah 2
    """, 'This is', 1,
        ),
    ],
)
def test_pattern_is_found_correctly(
        tmpdir: py.path.local,
        file_contents: str,
        pattern: str,
        n_matches: int,
):

    file = tmpdir.join('test.md')
    file.write(file_contents)

    search_mode = SearchMode()
    args = {
        'pattern': pattern,
        'path': file.strpath,
        'tag_str': None,
        'topic': None,
        'case_insensitive': False,
        'title': None,
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    search_mode.start(options)

    c = 0
    for match in search_mode.matches:
        for _ in match['matched_lines']:
            c += 1

    assert c == n_matches

# Handles empty files


def test_search_file_handles_empty_file(tmpdir: py.path.local):

    file = tmpdir.join('test.md')
    file.write('')

    search_mode = SearchMode()
    args = {
        'pattern': 'search term',
        'path': file.strpath,
        'tag_str': None,
        'topic': None,
        'case_insensitive': False,
        'title': None,
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    search_mode.start(options)
    assert len(search_mode.matches) == 0

# Pattern is matched but no tags found


def test_search_file_finds_pattern_but_not_tags(tmpdir: py.path.local):

    file = tmpdir.join('test.md')
    file.write('''---
                  tags: hi there
                  ---
                  # Heading 1
                  search term
               ''')

    search_mode = SearchMode()
    args = {
        'pattern': 'search term',
        'path': file.strpath,
        'tag_str': 'not in the file',
        'topic': None,
        'case_insensitive': False,
        'title': None,
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    search_mode.start(options)
    assert len(search_mode.matches) == 0


def test_search_file_pattern_and_tags_are_found(tmpdir: py.path.local):

    file = tmpdir.join('test.md')
    file.write('''---
                  tags: hi there
                  ---
                  # Heading 1
                  search term
               ''')

    search_mode = SearchMode()
    args = {
        'pattern': 'search term',
        'path': file.strpath,
        'tag_str': 'hi',
        'topic': None,
        'case_insensitive': False,
        'title': None,
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    search_mode.start(options)
    assert len(search_mode.matches) == 1

# Pattern is matched but no topic found


def test_search_file_finds_pattern_but_not_topic(tmpdir: py.path.local):

    file = tmpdir.join('test.md')
    file.write('''---
                  topic: test topic
                  ---
                  # Heading 1
                  search term
               ''')

    search_mode = SearchMode()
    args = {
        'pattern': 'search term',
        'path': file.strpath,
        'tag_str': None,
        'topic': 'not in the doc',
        'case_insensitive': False,
        'title': None,
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    search_mode.start(options)
    assert len(search_mode.matches) == 0


def test_search_file_pattern_and_topic_is_found(tmpdir: py.path.local):

    file = tmpdir.join('test.md')
    file.write('''---
                  topic: test topic
                  ---
                  # Heading 1
                  search term
               ''')

    search_mode = SearchMode()
    args = {
        'pattern': 'search term',
        'path': file.strpath,
        'tag_str': None,
        'topic': 'test topic',
        'case_insensitive': False,
        'title': None,
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    search_mode.start(options)
    assert len(search_mode.matches) == 1


def test_search_file_subject_is_found_as_topic(tmpdir: py.path.local):

    file = tmpdir.join('test.md')
    file.write('''---
                  subject: test topic
                  ---
                  # Heading 1
                  search term
               ''')

    search_mode = SearchMode()
    args = {
        'pattern': 'search term',
        'path': file.strpath,
        'tag_str': None,
        'topic': 'test topic',
        'case_insensitive': False,
        'title': None,
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    search_mode.start(options)
    assert len(search_mode.matches) == 1

# Pattern is matched but no title found


def test_search_file_finds_pattern_but_not_title(tmpdir: py.path.local):

    file = tmpdir.join('test.md')
    file.write('''---
                  title: Essay
                  ---
                  # Heading 1
                  search term
               ''')

    search_mode = SearchMode()
    args = {
        'pattern': 'search term',
        'path': file.strpath,
        'tag_str': None,
        'topic': None,
        'case_insensitive': False,
        'title': 'not in the doc',
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    search_mode.start(options)
    assert len(search_mode.matches) == 0


def test_search_file_pattern_and_title_is_found(tmpdir: py.path.local):

    file = tmpdir.join('test.md')
    file.write('''---
                  title: Essay
                  ---
                  # Heading 1
                  search term
               ''')

    search_mode = SearchMode()
    args = {
        'pattern': 'search term',
        'path': file.strpath,
        'tag_str': None,
        'topic': None,
        'case_insensitive': False,
        'title': 'essay',  # Note: is lowercase but should still be found
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    search_mode.start(options)
    assert len(search_mode.matches) == 1

# Case insensitive works


def test_search_file_case_insisitive_works_correctly(tmpdir: py.path.local):

    # Case sensitive (not found)
    file = tmpdir.join('test.md')
    file.write('''---
                  title: Essay
                  ---
                  # Heading 1
                  search TERM
               ''')

    search_mode = SearchMode()
    args = {
        'pattern': 'search term',
        'path': file.strpath,
        'tag_str': None,
        'topic': None,
        'case_insensitive': False,
        'title': None,
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    search_mode.start(options)
    assert len(search_mode.matches) == 0

    search_mode_i = SearchMode()
    args_i = {
        'pattern': 'search term',
        'path': file.strpath,
        'tag_str': None,
        'topic': None,
        'case_insensitive': True,
        'title': None,
    }
    options_i: ModeOptions = {
        'visual': True,
        'args': args_i,
    }
    search_mode_i.start(options_i)
    assert len(search_mode_i.matches) == 1

# Search dir


@patch('notesystem.modes.search_mode.SearchMode._search_file')
def test_search_dir_searches_all_md_files(mock: Mock, tmpdir: py.path.local):

    n_files = 5
    for i in range(5):
        file = tmpdir.join(f'test_file{i}.md')
        file.write('# Heading 1')

    search_mode = SearchMode()
    args = {
        'pattern': 'search term',
        'path': tmpdir.strpath,
        'tag_str': None,
        'topic': None,
        'case_insensitive': False,
        'title': None,
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    search_mode.start(options)
    assert mock.call_count == n_files


def test_search_dir_throws_error_when_not_dir(tmpdir: py.path.local):

    file = tmpdir.join('file.md')
    search_mode = SearchMode()
    with pytest.raises(NotADirectoryError):
        search_mode._search_dir(file.strpath)
