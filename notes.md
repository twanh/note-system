# TODO
- Auto formatter
	- Make sure there are newlines after **Bold text** if there is a list behind it
	- Remove empty bullet points
- Tests
	- Test the cli
		- Correct mode
		- Correct flags
		- Don't test the printing?

# Notes

## Pandoc flags:
```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--pandoc-args")

if __name__ == '__main__':
    args = parser.parse_args()

```
Use: `notesystem convert ... ... --pandoc-args="--flag1 --flag2 --flag3"`

# References;
- [Command based design pattern](https://refactoring.guru/design-patterns/command) -> Inpsiration for the modes.
