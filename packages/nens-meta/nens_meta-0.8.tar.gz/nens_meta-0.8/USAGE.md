# N&S project setup usage

There is a small number of tools/addons you have to install. They'll make life easier in all projects with the new setup.


## One-time install: two vscode plugins

- [Editorconfig plugin](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig). This one automatically reads the config in the `.editorconfig` file and configures line length, an "enter" at the end of the file, indentation, unneeded spaces. No need to do anything by hand anymore.
- [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python), of course.

(TODO: perhaps add ruff plugin, too? Unless it is already used in the python extension?)


## One-time install: one python package

Just pip-install them for your user. (My recommendation is to use [pipx](https://pipx.pypa.io/) to keep your python a bit cleaner, btw).

- `tox` (for running the test, the formatter, the checker and all sorts of other stuff you now no longer need to install by hand).
