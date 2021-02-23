# Notesystem

Notesystem takes away the struggle of having to convert markdown files to html using `pandoc` manually. It also has a checking mode which finds common markdown errors that occur when changing markdown flavours.

![example](https://media.giphy.com/media/wXPcBAWIELjRhMg8TQ/giphy.gif)

## Motivation for building notesystem
I have been taking notes in different ways over the years. I commonly use markdown for my notes but I have noticed that different software uses different flavours of markdown. For example dropbox paper an awesome online markdown note taking tool represents todo items without the dash. (`[ ] Todo` instead of `- [ ] Todo`). In pandoc markdown this is invalid and messes upt he whole document. The aim for this project is to be able to fix common markdown errors and convert markdown files quickly using pandoc.

## Current Checked Errors
| Error Name        | Short Description                                                                     | Checked | Auto fixable |
|-------------------|---------------------------------------------------------------------------------------|---------|--------------|
| Math Error        | Inline math is displayed with `$$...$$` instead of `$...$`                            | ✅       | ✅            |
| Separator Error   | No new line (`\n`) af a separator `---` (causes it to be rendered as a broken table). | ✅       | ✅            |
| Todo Error        | When there is no list indicator `-` before a todo item (`[ ] Todo`)                   | ✅       | ✅            |
| List Indent Error | When the root node of a list starts with indentation it is rendered as a code block   | ✅       | ❌            |
