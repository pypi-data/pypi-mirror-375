"""Test pretty printing of configurations."""

import pytest

from configaroo import Configuration, print_configuration
from tests.schema import ConfigSchema


def test_printing_of_config(
    capsys: pytest.CaptureFixture[str], config: Configuration
) -> None:
    """Test that a configuration can be printed."""
    print_configuration(config, indent=4)
    stdout = capsys.readouterr().out
    lines = stdout.splitlines()

    assert "- number: 42" in lines
    assert "- word: 'platypus'" in lines
    assert "- nested" in lines
    assert "    - pie: 3.14" in lines


def test_indentation(capsys: pytest.CaptureFixture[str], config: Configuration) -> None:
    """Test that indentation can be controlled."""
    print_configuration(config, indent=7)
    stdout = capsys.readouterr().out
    lines = stdout.splitlines()

    assert "       - pie: 3.14" in lines


def test_printing_of_basemodel(
    capsys: pytest.CaptureFixture[str], config: Configuration, model: type[ConfigSchema]
) -> None:
    """Test that a configuration converted into a BaseModel can be printed."""
    print_configuration(config.with_model(model))
    stdout = capsys.readouterr().out
    lines = stdout.splitlines()

    assert "- number: 42" in lines
    assert "- word: 'platypus'" in lines
    assert "- nested" in lines
    assert "    - pie: 3.14" in lines


def test_printing_of_dynamic_values(
    capsys: pytest.CaptureFixture[str], config: Configuration
) -> None:
    """Test that interpolated values are printed correctly."""
    print_configuration(config.parse_dynamic({"message": "testing configaroo"}))
    stdout = capsys.readouterr().out
    lines = stdout.splitlines()

    assert "- number: 42" in lines
    assert "- phrase: 'The meaning of life is 42'" in lines
    assert "    - format: '<level>{level:<8} testing configaroo</level>'" in lines


def test_printing_of_existing_section(
    capsys: pytest.CaptureFixture[str], config: Configuration
) -> None:
    """Test that sections can be printed."""
    print_configuration(config, section="paths")
    stdout = capsys.readouterr().out
    lines = stdout.splitlines()

    assert "- absolute: '/home/configaroo'" in lines
    assert "- number: 42" not in lines


def test_printing_of_nonexisting_section(config: Configuration) -> None:
    """Test that non-existing sections raise an error."""
    with pytest.raises(KeyError):
        print_configuration(config, section="nonexisting")


def test_printing_of_values(
    capsys: pytest.CaptureFixture[str], config: Configuration
) -> None:
    """Test that individual values can be printed."""
    print_configuration(config, section="number")
    stdout = capsys.readouterr().out
    lines = stdout.splitlines()

    assert lines == ["- number: 42"]


def test_printing_of_nested_sections(
    capsys: pytest.CaptureFixture[str], config: Configuration
) -> None:
    """Test that nested sections can be printed."""
    print_configuration(config, section="nested.deep")
    stdout = capsys.readouterr().out
    lines = stdout.splitlines()

    assert lines == ["- sea: 'Marianer'"]


def test_printing_of_rich_markup(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that a config value containing malformed Rich markup can be printed."""
    config = Configuration({"markup": "[/]"})
    print_configuration(config)
    stdout = capsys.readouterr().out

    assert stdout.strip() == "- markup: '[/]'"


def test_print_keeping_none(
    capsys: pytest.CaptureFixture[str], config: Configuration
) -> None:
    """Test that None-values are kept in printout by default."""
    print_configuration(config | {"none": None})
    stdout = capsys.readouterr().out
    lines = stdout.splitlines()

    assert "- none: None" in lines
    assert "- number: 42" in lines


def test_print_skipping_none(
    capsys: pytest.CaptureFixture[str], config: Configuration
) -> None:
    """Test that None-values are skipped in printout if asked for."""
    config.update({"none": None})
    config.nested.deep.update({"sea": "Mjoesa", "depth": None})
    print_configuration(config, skip_none=True)
    stdout = capsys.readouterr().out
    lines = stdout.splitlines()

    assert "- none: None" not in lines
    assert "        - depth: None" not in lines
    assert "- number: 42" in lines
