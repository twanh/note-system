# Notesystem Notesystem takes away the struggle of having to convert markdown files to html using `pandoc` manually. It also has a checking mode which finds common markdown errors that occur when changing markdown flavours.  ![example](https://media.giphy.com/media/wXPcBAWIELjRhMg8TQ/giphy.gif) ## Motivation for building notesystem I have been taking notes in different ways over the years. I commonly use markdown for my notes but I have noticed that different software uses different flavours of markdown. For example dropbox paper an awesome online markdown note taking tool represents todo items without the dash. (`[ ] Todo` instead of `- [ ] Todo`). In pandoc markdown this is invalid and messes up the whole document. The aim for this project is to be able to fix common markdown errors and convert markdown files quickly using pandoc.  ## Installation _Because notesystem still is in development there is no prebuild package available yet._ Clone this github repository: ``` $ git clone git@github.com:twanh/note-system ```
Install the requirements:
_It is recommended to use a virtual environment for the following steps_
```
pip install -r requirements.txt
```
At this point you can run notesystem using:
```
python -m notesystem
```
To install notesystem for usage outside of the notesystem git directory run:
```
pip install .
```
Now you can use notesystem everywhere by running:
```
notesystem --help
```

## Current Checked Errors
| Error Name        | Short Description                                                                     | Checked | Auto fixable |
|-------------------|---------------------------------------------------------------------------------------|---------|--------------|
| Math Error        | Inline math is displayed with `$$...$$` instead of `$...$`                            | ✅       | ✅            |
| Separator Error   | No new line (`\n`) af a separator `---` (causes it to be rendered as a broken table). | ✅       | ✅            |
| Todo Error        | When there is no list indicator `-` before a todo item (`[ ] Todo`)                   | ✅       | ✅            |
| List Indent Error | When the root node of a list starts with indentation it is rendered as a code block   | ✅       | ❌            |
