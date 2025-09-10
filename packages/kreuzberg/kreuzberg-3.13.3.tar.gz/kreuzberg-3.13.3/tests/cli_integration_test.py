from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import click  # noqa: F401
    import rich  # noqa: F401

    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False

pytestmark = pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI dependencies not installed")


IS_CI = os.environ.get("CI", "false").lower() == "true"


def test_cli_extract_html_file(tmp_path: Path) -> None:
    html_file = tmp_path / "test.html"
    html_file.write_text("""
    <html>
        <head><title>Test Document</title></head>
        <body>
            <h1>Test Heading</h1>
            <p>This is a test paragraph with some content.</p>
            <p>Another paragraph for testing.</p>
        </body>
    </html>
    """)

    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", str(html_file)],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "Test Heading" in result.stdout
    assert "test paragraph" in result.stdout
    assert "Another paragraph" in result.stdout


def test_cli_extract_to_file(tmp_path: Path) -> None:
    md_file = tmp_path / "test.md"
    md_file.write_text("""
    # Test Markdown

    This is a **test** markdown file with some content.

    - Item 1
    - Item 2
    - Item 3
    """)

    output_file = tmp_path / "output.txt"

    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", str(md_file), "-o", str(output_file)],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert output_file.exists()

    content = output_file.read_text()
    assert "Test Markdown" in content
    assert "**test** markdown file" in content
    assert "Item 1" in content


def test_cli_extract_json_output_with_metadata(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("This is a simple text file for testing JSON output.")

    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", str(txt_file), "--output-format", "json", "--show-metadata"],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0

    output_data = json.loads(result.stdout)
    assert "content" in output_data
    assert "mime_type" in output_data
    assert "metadata" in output_data
    assert "simple text file" in output_data["content"]


def test_cli_extract_from_stdin() -> None:
    test_content = "<html><body><h1>Stdin Test</h1><p>Content from stdin</p></body></html>"

    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract"],
        check=False,
        input=test_content,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "Stdin Test" in result.stdout
    assert "Content from stdin" in result.stdout


def test_cli_with_config_file(tmp_path: Path) -> None:
    html_file = tmp_path / "test.html"
    html_file.write_text("<html><body><p>Test content for config</p></body></html>")

    config_file = tmp_path / "pyproject.toml"
    config_file.write_text("""
[tool.kreuzberg]
chunk_content = true
max_chars = 200
max_overlap = 50
extract_tables = false

[tool.kreuzberg.tesseract]
language = "eng"
psm = 6
""")

    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", str(html_file), "--config", str(config_file), "--verbose"],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "Test content" in result.stdout


def test_cli_config_command(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text("""
[tool.kreuzberg]
force_ocr = true
chunk_content = false
max_chars = 5000

[tool.kreuzberg.tesseract]
language = "eng+deu"
psm = 3
""")

    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "config", "--config", str(config_file)],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0

    output_text = result.stderr
    assert "force_ocr" in output_text
    assert "true" in output_text
    assert "eng+deu" in output_text
    assert "config.toml" in output_text


def test_cli_config_command_no_file(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "config"], check=False, capture_output=True, text=True, cwd=tmp_path
    )

    assert result.returncode == 0
    assert "No configuration file found" in result.stderr
    assert "Default configuration values" in result.stderr


def test_cli_tesseract_options(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Simple text content for tesseract options test.")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kreuzberg",
            "extract",
            str(txt_file),
            "--ocr-backend",
            "tesseract",
            "--tesseract-lang",
            "eng",
            "--tesseract-psm",
            "6",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "Simple text content" in result.stdout


def test_cli_force_ocr_option(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Text content that should be processed with OCR.")

    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", str(txt_file), "--force-ocr", "--ocr-backend", "tesseract"],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "processed with OCR" in result.stdout


def test_cli_chunking_options(tmp_path: Path) -> None:
    txt_file = tmp_path / "long_text.txt"
    long_text = "This is a test. " * 200
    txt_file.write_text(long_text)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kreuzberg",
            "extract",
            str(txt_file),
            "--chunk-content",
            "--max-chars",
            "200",
            "--max-overlap",
            "50",
            "--output-format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0

    output_data = json.loads(result.stdout)

    assert "content" in output_data


def test_cli_auto_config_detection(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Content for auto config test.")

    config_file = tmp_path / "pyproject.toml"
    config_file.write_text("""
[tool.kreuzberg]
max_chars = 1500
""")

    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", str(txt_file), "--verbose"],
        check=False,
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    assert result.returncode == 0
    assert "Content for auto config" in result.stdout


def test_cli_error_invalid_file() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", "nonexistent.pdf"],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode != 0
    assert "does not exist" in result.stderr


def test_cli_error_invalid_ocr_backend(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Test content")

    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", str(txt_file), "--ocr-backend", "invalid_backend"],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode != 0
    assert "Invalid OCR backend" in result.stderr


def test_cli_version_command() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "--version"],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "kreuzberg, version" in result.stdout

    import re

    assert re.search(r"\d+\.\d+\.\d+", result.stdout), f"No version pattern found in: {result.stdout}"


def test_cli_help_command() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "--help"], check=False, capture_output=True, text=True, cwd=Path.cwd()
    )

    assert result.returncode == 0
    assert "Kreuzberg - Text extraction from documents" in result.stdout
    assert "extract" in result.stdout
    assert "config" in result.stdout


def test_cli_extract_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", "--help"],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "Extract text from a document" in result.stdout
    assert "--force-ocr" in result.stdout
    assert "--chunk-content" in result.stdout
    assert "--extract-tables" in result.stdout


@pytest.mark.xfail(IS_CI, reason="OCR tests may fail in CI due to Tesseract issues")
def test_cli_with_real_pdf(tmp_path: Path) -> None:
    pdf_files = list(Path("tests/test_source_files").glob("*.pdf"))
    if not pdf_files:
        pytest.skip("No PDF test files available")

    pdf_file = pdf_files[0]
    output_file = tmp_path / "pdf_output.txt"

    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", str(pdf_file), "-o", str(output_file)],
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=Path.cwd(),
    )

    if result.returncode < 0:
        pytest.skip(f"PDF extraction terminated by signal {-result.returncode}")

    assert result.returncode == 0
    assert output_file.exists()

    content = output_file.read_text()
    assert len(content.strip()) > 0


def test_cli_extract_tables_option(tmp_path: Path) -> None:
    html_file = tmp_path / "table_test.html"
    html_file.write_text("""
    <html>
        <body>
            <h1>Document with Table</h1>
            <table>
                <tr><th>Name</th><th>Age</th></tr>
                <tr><td>John</td><td>30</td></tr>
                <tr><td>Jane</td><td>25</td></tr>
            </table>
        </body>
    </html>
    """)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kreuzberg",
            "extract",
            str(html_file),
            "--extract-tables",
            "--output-format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0

    output_data = json.loads(result.stdout)
    assert "content" in output_data
    assert "Document with Table" in output_data["content"]


def test_cli_configuration_precedence(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Test content for precedence check.")

    config_file = tmp_path / "test_config.toml"
    config_file.write_text("""
[tool.kreuzberg]
chunk_content = false
max_chars = 1000
""")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kreuzberg",
            "extract",
            str(txt_file),
            "--config",
            str(config_file),
            "--chunk-content",
            "--output-format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0

    output_data = json.loads(result.stdout)
    assert "precedence check" in output_data["content"]


def test_cli_invalid_config_file(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Test content")

    bad_config = tmp_path / "bad_config.toml"
    bad_config.write_text("invalid toml content [[[")

    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", str(txt_file), "--config", str(bad_config)],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 1
    assert "Invalid TOML" in result.stderr


def test_cli_missing_config_file(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Test content")

    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", str(txt_file), "--config", "nonexistent_config.toml"],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 2
    assert "does not exist" in result.stderr


def test_cli_ocr_backend_none(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Simple text that should not use OCR.")

    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", str(txt_file), "--ocr-backend", "none"],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "should not use OCR" in result.stdout


def test_cli_tesseract_output_format_text(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Text for Tesseract text format testing.")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kreuzberg",
            "extract",
            str(txt_file),
            "--ocr-backend",
            "tesseract",
            "--tesseract-output-format",
            "text",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "Tesseract text format" in result.stdout


def test_cli_tesseract_output_format_markdown(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Text for **markdown** format testing.")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kreuzberg",
            "extract",
            str(txt_file),
            "--ocr-backend",
            "tesseract",
            "--tesseract-output-format",
            "markdown",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "markdown" in result.stdout


def test_cli_tesseract_output_format_tsv(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Text for TSV format testing.")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kreuzberg",
            "extract",
            str(txt_file),
            "--ocr-backend",
            "tesseract",
            "--tesseract-output-format",
            "tsv",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "TSV format" in result.stdout


def test_cli_tesseract_output_format_hocr(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Text for hOCR format testing.")

    output_file = tmp_path / "output.html"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kreuzberg",
            "extract",
            str(txt_file),
            "--ocr-backend",
            "tesseract",
            "--tesseract-output-format",
            "hocr",
            "-o",
            str(output_file),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert output_file.exists()
    content = output_file.read_text()
    assert "hOCR format" in content


def test_cli_enable_table_detection(tmp_path: Path) -> None:
    html_file = tmp_path / "table.html"
    html_file.write_text("""
    <html>
        <body>
            <table>
                <tr><th>Product</th><th>Price</th></tr>
                <tr><td>Apple</td><td>$1.00</td></tr>
                <tr><td>Orange</td><td>$0.80</td></tr>
            </table>
        </body>
    </html>
    """)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kreuzberg",
            "extract",
            str(html_file),
            "--ocr-backend",
            "tesseract",
            "--tesseract-output-format",
            "tsv",
            "--enable-table-detection",
            "--output-format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    output_data = json.loads(result.stdout)
    assert "content" in output_data
    assert "Product" in output_data["content"]
    assert "Apple" in output_data["content"]


def test_cli_tesseract_with_image_file(tmp_path: Path) -> None:
    image_files = list(Path("tests/test_source_files").glob("*.png"))
    if not image_files:
        pytest.skip("No PNG test files available")

    image_file = image_files[0]

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kreuzberg",
            "extract",
            str(image_file),
            "--ocr-backend",
            "tesseract",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=Path.cwd(),
    )

    if result.returncode < 0:
        pytest.skip(f"Image extraction terminated by signal {-result.returncode}")

    assert result.returncode == 0
    assert len(result.stdout.strip()) > 0


def test_cli_table_detection_with_tsv(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Simple text with potential table structure.")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kreuzberg",
            "extract",
            str(txt_file),
            "--ocr-backend",
            "tesseract",
            "--tesseract-output-format",
            "tsv",
            "--enable-table-detection",
            "--output-format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    output_data = json.loads(result.stdout)
    assert "content" in output_data
    assert "Simple text" in output_data["content"]


def test_cli_all_tesseract_options_combined(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Comprehensive Tesseract options test.")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kreuzberg",
            "extract",
            str(txt_file),
            "--ocr-backend",
            "tesseract",
            "--tesseract-lang",
            "eng",
            "--tesseract-psm",
            "6",
            "--tesseract-output-format",
            "markdown",
            "--enable-table-detection",
            "--force-ocr",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "Comprehensive Tesseract" in result.stdout


def test_cli_help_shows_new_options() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", "--help"],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "--tesseract-output-format" in result.stdout
    assert "--enable-table-detection" in result.stdout
    assert "markdown" in result.stdout
    assert "tsv" in result.stdout
    assert "hocr" in result.stdout


def test_cli_config_with_tesseract_output_format(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Config test content.")

    config_file = tmp_path / "pyproject.toml"
    config_file.write_text("""
[tool.kreuzberg]
force_ocr = false
ocr_backend = "tesseract"

[tool.kreuzberg.tesseract]
output_format = "markdown"
enable_table_detection = false
language = "eng"
""")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kreuzberg",
            "extract",
            str(txt_file),
            "--config",
            str(config_file),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "Config test content" in result.stdout


def test_cli_invalid_tesseract_output_format(tmp_path: Path) -> None:
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Test content")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kreuzberg",
            "extract",
            str(txt_file),
            "--tesseract-output-format",
            "invalid",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode != 0
    assert "Invalid value" in result.stderr or "invalid" in result.stderr


def test_cli_unicode_character_handling(tmp_path: Path) -> None:
    txt_file = tmp_path / "unicode_test.txt"
    unicode_content = "Test with Unicode: — (em dash) ― (horizontal bar U+2015) • (bullet) € (euro) 中文 (Chinese)"
    txt_file.write_text(unicode_content, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "kreuzberg", "extract", str(txt_file)],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert "—" in result.stdout
    assert "―" in result.stdout
    assert "•" in result.stdout
    assert "€" in result.stdout
    assert "中文" in result.stdout
