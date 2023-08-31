# Installation
We recommend installing within a [virtual environment](https://docs.python.org/3/tutorial/venv.html) in order to not alter any python distribution files on your machine.

## Linux/Mac OS

To install BPX on Linux/Mac OS use the following terminal commands:

1. Create a virtual environment

```bash
virtualenv env
```

2. Activate the virtual environment

```bash
source env/bin/activate
```

3. Install the `bpx` package

```bash
pip install bpx
```

## Windows

To install BPX on Windows use the following commands:

1. Create a virtual environment

```bash
python -m virtualenv env
```

2. Activate the virtual environment

```bash
env\Scripts\activate
```

where `env` is the path to the environment created in step 3 (e.g. `C:\Users\'Username'\env\Scripts\activate.bat`).

3. Install the `bpx` package

```bash
pip install bpx
```

As an alternative, you can set up [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/about). This allows you to run a full Linux distribution within Windows.
