# Notesystem
[![NoteSystem](https://github.com/twanh/note-system/actions/workflows/python_actions.yml/badge.svg)](https://github.com/twanh/note-system/actions/workflows/python_actions.yml)

Notesystem takes away the struggle of having to convert markdown files to html using `pandoc` manually. It also has a checking mode which finds common markdown errors that occur when changing markdown flavours.
![example](https://media.giphy.com/media/wXPcBAWIELjRhMg8TQ/giphy.gif)

## Motivation for building notesystem
I have been taking notes in different ways over the years. I commonly use markdown for my notes but I have noticed that different software uses different flavours of markdown. For example dropbox paper an awesome online markdown note taking tool represents todo items without the dash. (`[ ] Todo` instead of `- [ ] Todo`). In pandoc markdown this is invalid and messes up the whole document. The aim for this project is to be able to fix common markdown errors and convert markdown files quickly using pandoc.

## Usage and Features
Notesystem is build to firstly convert and seccondly find and fix errors in markdown files.

The currently supported errors are:
| Error Name        | Short Description                                                                     | Checked | Auto fixable |
|-------------------|---------------------------------------------------------------------------------------|---------|--------------|
| Math Error        | Inline math is displayed with `$$...$$` instead of `$...$`                            | ✅       | ✅            |
| Separator Error   | No new line (`\n`) af a separator `---` (causes it to be rendered as a broken table). | ✅       | ✅            |
| Todo Error        | When there is no list indicator `-` before a todo item (`[ ] Todo`)                   | ✅       | ✅            |
| List Indent Error | When the root node of a list starts with indentation it is rendered as a code block   | ✅       | ❌            |

### Checking
Notesystem can check for common errors (see above which errors are supported) and fix them automatically.
```
usage: notesystem check [-h] [--fix] in

positional arguments:
  in          the file/folder to be checked

optional arguments:
  -h, --help  show this help message and exit
  --fix, -f   enables auto fixing for problems in the documents

```


### Converting
Notesystem converts markdown files to html files using pandoc. When given a directory notesystem converts all the files inside the directory. Also all the files in the subdirectories are converted and the directory is copied to the output directory.

```console
usage: notesystem convert [-h] [--watch] [--pandoc-args ARGS] in out

positional arguments:
  in                  the file/folder to be converted
  out                 the path to write the converted file(s) to

optional arguments:
  -h, --help          show this help message and exit
  --watch, -w         enables watch mode (convert files that have changed as
                      soon as they have changed)
  --pandoc-args ARGS  specify the arguments that need to based on to pandoc.
                      E.g.: --pandoc-args='--standalone --preserve-tabs'

```

For example: `notesystem convert notes html_notes` would convert all markdown files inside the folder `notes` to html and save them to the folder `html_notes`

#### Watch mode
Watch mode watches the given directory or file and triggers a convert when a file is changed or created.
Note: before watching is started all files are converted first.

For example: `notesystem convert notes html_notes -w` would firstly convert all files and then watch the directory for changes



## Installation
_Because notesystem still is in development there is no prebuild package available yet._

### Prerequisites
Make sure you have pandoc installed already. For instructions to install pandoc see [their documentation](https://github.com/jgm/pandoc/blob/master/INSTALL.md)

After pandoc is installed install the GitHub.html5 template. For installation instructions see [their documentation](https://github.com/tajmone/pandoc-goodies/tree/master/templates/html5/github)

### Installation

Clone this github repository:
```
$ git clone git@github.com:twanh/note-system
```

Install the requirements:
_It is recommended to use a virtual environment for the following steps_
```
$ pip install -r requirements.txt
```

At this point you can run notesystem using:
```
python -m notesystem --help
```
To install notesystem for usage outside of the notesystem git directory run:
```
pip install .
```
Now you can use notesystem everywhere by running:
```
notesystem --help
```
