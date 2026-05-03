# dictionary-cli

Small Python CLI for looking up dictionary definitions and thesaurus results from Merriam-Webster and rendering them with `glow`.

## Description

`dict` looks up a word in the thesaurus API first, falls back to the dictionary API when needed, and caches lookup results under `~/.cache/dict/lookups`.

The script currently expects API keys to be available through the 1Password CLI with these item paths:

- `op://Personal/Dictionary API/Dictionary API Key`
- `op://Personal/Dictionary API/Thesaurus API Key`

It also shells out to `glow` to render formatted terminal output.

## Requirements

- Python 3
- `op` (1Password CLI)
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
pytest tests/test_dict.py
```

Or:

```bash
python3 -m pytest tests/test_dict.py
```

Run all tests in the test directory with:

```bash
pytest tests
```

## GitHub Actions

CI is configured in `.github/workflows/tests.yml` and runs the unit tests on every push and pull request.
