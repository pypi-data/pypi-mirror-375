# dispcat

![](https://www.catbehaviourist.com/wp-content/uploads/2015/07/amazing-black-cats_1024-1.jpg)

**dispcat** is a simple CLI tool that displays random cat images in separate windows on your screen. You can choose how many cats to display and optionally hide the OS window toolbar for a frameless experience.

## Features

- Display one or more random cat images in separate windows
- Option to hide the OS window toolbar (frameless mode)
- Fast and easy to use from the command line

## Installation

You need Python 3.10 or higher.

Install using [Poetry](https://python-poetry.org/):

```sh
poetry install
```

Or install directly with pip:

```sh
pip install dispcat
```

## Usage

Run the following command to display a cat:

```sh
dispcat
```

To display multiple cats:

```sh
dispcat --count 5
```

To display cats in frameless windows:

```sh
dispcat --frameless
```

You can combine options:

```sh
dispcat --count 3 --frameless
```

## Options

| Option         | Description                                      | Default |
|----------------|--------------------------------------------------|---------|
| `--count`      | Number of cat images to display                  | 1       |
| `--frameless`  | Hide OS window toolbar (frameless mode)          | False   |
