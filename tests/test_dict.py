import importlib.util
from importlib.machinery import SourceFileLoader
import sys
from pathlib import Path

import pytest

class DummyResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


@pytest.fixture
def dict_module(monkeypatch, tmp_path):
    module_name = "dict_under_test"
    module_path = Path(__file__).resolve().parents[1] / "dict"

    monkeypatch.setattr("subprocess.check_output", lambda *args, **kwargs: "test-key")
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    monkeypatch.setattr(
        "requests.get",
        lambda *args, **kwargs: DummyResponse(
            [
                {
                    "hwi": {"hw": "placeholder"},
                    "fl": "noun",
                    "shortdef": ["placeholder definition"],
                }
            ]
        ),
    )
    monkeypatch.setattr("os.system", lambda *args, **kwargs: 0)
    monkeypatch.setattr(sys, "argv", ["dict", "placeholder"])

    loader = SourceFileLoader(module_name, str(module_path))
    spec = importlib.util.spec_from_loader(module_name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules.pop(module_name, None)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)

    module.cache.clear()

    yield module

    sys.modules.pop(module_name, None)


def test_flatten_word_lists_prefers_variant_forms(dict_module):
    nested = [
        [{"wd": "home"}, {"wd": "abode", "wvrs": [{"wva": "abodes"}]}],
        [{"wd": "house"}],
    ]

    assert dict_module.SynonymResult._flatten_word_lists(nested) == ["home", "abodes", "house"]


def test_from_api_entry_collects_synonyms_related_and_antonyms(dict_module):
    entry = {
        "hwi": {"hw": "bright"},
        "fl": "adjective",
        "shortdef": ["giving off light", "clever"],
        "meta": {"ants": [["dim"]]},
        "def": [
            {
                "sseq": [
                    [
                        [
                            "sense",
                            {
                                "syn_list": [[{"wd": "brilliant"}]],
                                "rel_list": [[{"wd": "radiant"}]],
                            },
                        ]
                    ]
                ]
            }
        ],
    }

    result = dict_module.SynonymResult.from_api_entry(entry)

    assert result.word == "bright"
    assert result.part_of_speech == "adjective"
    assert result.definitions == ["giving off light", "clever"]
    assert result.syns == ["brilliant"]
    assert result.related == ["radiant"]
    assert result.antonyms == ["dim"]

def test_str_escapes_asterisk(dict_module):
    result = dict_module.SynonymResult(
        word="co*op",
        part_of_speech="noun",
        definitions=["a cooperative arrangement"],
        syns=["collective"],
        related=["partnership"],
        antonyms=[],
    )

    rendered = str(result)

    assert "co\\*op" in rendered


def test_str_includes_related_words_when_enabled(dict_module):
    result = dict_module.SynonymResult(
        word="ally",
        part_of_speech="noun",
        definitions=["one associated with another"],
        syns=["friend"],
        related=["partner"],
        antonyms=[],
    )

    dict_module.show_related = True

    assert "## Related words:\n  partner" in str(result)


def test_lookup_synonyms_falls_back_to_dictionary_for_suggestions(dict_module, monkeypatch):
    monkeypatch.setattr(dict_module.requests, "get", lambda *args, **kwargs: DummyResponse(["maybe-this"]))
    monkeypatch.setattr(dict_module, "lookup_dictionary", lambda word: [f"dict:{word}"])

    assert dict_module.lookup_synonyms("missing") == ["dict:missing"]


def test_lookup_dictionary_retries_with_first_suggestion(dict_module, monkeypatch):
    responses = iter([
        ["suggestion", "other"],
        [{"hwi": {"hw": "suggestion"}, "fl": "noun", "shortdef": ["replacement"]}],
    ])

    monkeypatch.setattr(dict_module.requests, "get", lambda *args, **kwargs: DummyResponse(next(responses)))
    os_calls = []
    monkeypatch.setattr(dict_module.os, "system", os_calls.append)

    results = dict_module.lookup_dictionary("mispell")

    assert [result.word for result in results] == ["suggestion"]
    assert any("Searching for suggestion" in call for call in os_calls)


def test_lookup_uses_cache_before_http_fetch(dict_module, monkeypatch):
    cached = dict_module.SynonymResult(
        word="cached",
        part_of_speech="noun",
        definitions=["stored result"],
        syns=["saved"],
        related=[],
        antonyms=[],
    )
    dict_module.cache.set("cached", [cached.to_dict()])

    def fail_lookup(_word):
        raise AssertionError("lookup_synonyms should not be called when cache exists")

    monkeypatch.setattr(dict_module, "lookup_synonyms", fail_lookup)

    results = dict_module.lookup("cached")

    assert len(results) == 1
    assert isinstance(results[0], dict_module.SynonymResult)
    assert results[0].word == "cached"


def test_lookup_fetches_and_saves_when_cache_misses(dict_module, monkeypatch):
    fresh = dict_module.SynonymResult(
        word="fresh",
        part_of_speech="adjective",
        definitions=["newly fetched"],
        syns=["new"],
        related=[],
        antonyms=[],
    )

    saved = {"called": False}
    monkeypatch.setattr(dict_module, "lookup_synonyms", lambda word: [fresh])
    monkeypatch.setattr(dict_module.cache, "save", lambda: saved.__setitem__("called", True))

    results = dict_module.lookup("fresh")

    assert results == [fresh]
    assert dict_module.cache.get("fresh") == [fresh.to_dict()]
    assert saved["called"] is True
