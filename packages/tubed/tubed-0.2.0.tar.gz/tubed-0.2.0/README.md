# Youtube downloader CLI

![build](https://github.com/MousaZeidBaker/tubed/workflows/Publish/badge.svg)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
![python_version](https://img.shields.io/badge/python-%3E=3.9-blue)
[![pypi_v](https://img.shields.io/pypi/v/tubed)](https://pypi.org/project/tubed)

## Usage

Show help message and exit
```shell
tubed --help
```

Download video from URL
```shell
tubed --url https://www.youtube.com/watch?v=xFrGuyw1V8s
```

Download only audio
```shell
tubed --url https://www.youtube.com/watch?v=xFrGuyw1V8s --only-audio
```

Download from URLs specified in the [example.txt](./playlists/example.txt)
file
```shell
tubed --url-file playlists/example.txt
```

## Contributing
Contributions are welcome via pull requests.

## Issues
If you encounter any problems, please file an
[issue](https://github.com/MousaZeidBaker/tubed/issues) along with a detailed
description.

## Develop
Activate virtual environment
```shell
poetry shell
```

Install dependencies
```shell
poetry install --remove-untracked
```

Install git hooks
```shell
pre-commit install --hook-type pre-commit
```

Run linter
```shell
flake8 .
```

Format code
```shell
black .
```

Sort imports
```shell
isort .
```

Install current project from branch
```shell
poetry add git+https://github.com/MousaZeidBaker/tubed.git#branch-name
```
