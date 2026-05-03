# dictionary-cli

Small Python CLI for looking up dictionary definitions and thesaurus results from [Merriam-Webster](https://dictionaryapi.com/) and rendering them with [glow](https://github.com/charmbracelet/glow).

## Description

`dict` looks up a word in the thesaurus API first, falls back to the dictionary API when needed, and caches lookup results under `~/.cache/dict/lookups`.

It also shells out to [glow](https://github.com/charmbracelet/glow) (if it is installed) to render formatted terminal output.

## Requirements

- Python 3.11+

### Optional

- `glow`

Install Python dependencies with:

```bash
python3 -m pip install -r requirements.txt
```

## CLI Usage

Basic lookup:

```bash
./dict heterogeneous
```

Show related words:

```bash
./dict heterogeneous --show-related
```

Limit results:

```bash
./dict heterogeneous --limit 3
```

Disable cache for a lookup:

```bash
./dict heterogeneous --no-cache
```

Clear the local cache:

```bash
./dict --clear-cache
```

Debug output:

```bash
./dict heterogeneous --debug
```

Supported flags:

- `--show-related`, `-r`
- `--limit`, `-l`
- `--no-cache`
- `--clear-cache`, `--cache-clear`
- `--debug`, `-d`

## Testing

Run the unit tests with:

```bash
pytest tests
```
