# CE
A very simple C-like language.


## How-to

### Requirements

#### Venv (optional)
I recommend using python `venv`:
```sh
$ python -m venv venv && source ./venv/bin/activate
```

#### Dependencies
The dependencies are defined in `requirements.txt`. They are:
- `llvmlite`, for code generation and some compilation;
- `ply`, for lexing and parsing hte language;
- `flake8`, for linting;
- `coverage`, for code test coverage (not used much).

```sh
(venv) $ pip install -r requirements.txt
```

### Execute

Place the code inside `example.ce` and execute:
```sh
(venv) $ make compile
```

It will generate an `a.out` with `gcc`. Or, if you prefer, you can execute:
```sh
(venv) $ python main.py -f example.ce > out.ir
(venv) $ lli out.ir
```
It will output the intermediary code into the file and run it with the `llvm` interpreter.
