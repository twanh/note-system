# TODO
- Only convert files that have been changed
- Auto formatter
	- Make sure there are newlines after **Bold text** if there is a list behind it
	- Remove empty bullet pointsheadingsheadings
	- Indented lists `    -` are treaded as codeblock -> remove the indentation
			- Basic validation done
			- Should check current line, next and previous???
			- The test are also not good enough, they test basic use case but not
				fulldoc scan
