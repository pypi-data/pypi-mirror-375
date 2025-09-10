from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from kreuzberg import ExtractionConfig
from kreuzberg._types import ExtractionResult
from kreuzberg.extraction import (
    batch_extract_bytes,
    batch_extract_bytes_sync,
    batch_extract_file,
    batch_extract_file_sync,
)


@pytest.fixture
def test_files(tmp_path: Path) -> list[Path]:
    files = []
    for i in range(3):
        file_path = tmp_path / f"test_{i}.txt"
        file_path.write_text(f"Test content {i}")
        files.append(file_path)
    return files


@pytest.fixture
def test_bytes() -> list[tuple[bytes, str]]:
    return [
        (b"Test content 1", "text/plain"),
        (b"Test content 2", "text/plain"),
        (b"Test content 3", "text/plain"),
    ]


@pytest.mark.anyio
async def test_batch_extract_file_empty() -> None:
    results = await batch_extract_file([])
    assert results == []


@pytest.mark.anyio
async def test_batch_extract_file_single(test_files: list[Path]) -> None:
    results = await batch_extract_file([test_files[0]])
    assert len(results) == 1
    assert results[0].content == "Test content 0"


@pytest.mark.anyio
async def test_batch_extract_file_multiple(test_files: list[Path]) -> None:
    results = await batch_extract_file(test_files)
    assert len(results) == 3
    for i, result in enumerate(results):
        assert result.content == f"Test content {i}"


@pytest.mark.anyio
async def test_batch_extract_file_with_error() -> None:
    async def mock_extract_file(file_path: Path, mime_type: Any, config: Any) -> ExtractionResult:
        if file_path == Path("file1"):
            return ExtractionResult(content="OK1", mime_type="text/plain", metadata={}, chunks=[])
        if file_path == Path("file2"):
            raise RuntimeError("Extract failed")

        return ExtractionResult(content="OK3", mime_type="text/plain", metadata={}, chunks=[])

    with patch("kreuzberg.extraction.extract_file", side_effect=mock_extract_file):
        results = await batch_extract_file([Path("file1"), Path("file2"), Path("file3")])

        assert len(results) == 3
        assert results[0].content == "OK1"
        assert "Error: RuntimeError: Extract failed" in results[1].content
        assert results[1].metadata.get("error") is not None
        assert results[2].content == "OK3"


@pytest.mark.anyio
async def test_batch_extract_bytes_empty() -> None:
    results = await batch_extract_bytes([])
    assert results == []


@pytest.mark.anyio
async def test_batch_extract_bytes_single(test_bytes: list[tuple[bytes, str]]) -> None:
    results = await batch_extract_bytes([test_bytes[0]])
    assert len(results) == 1
    assert "Test content 1" in results[0].content


@pytest.mark.anyio
async def test_batch_extract_bytes_multiple(test_bytes: list[tuple[bytes, str]]) -> None:
    results = await batch_extract_bytes(test_bytes)
    assert len(results) == 3
    for i, result in enumerate(results):
        assert f"Test content {i + 1}" in result.content


def test_batch_extract_file_sync_empty() -> None:
    results = batch_extract_file_sync([])
    assert results == []


def test_batch_extract_file_sync_single(test_files: list[Path]) -> None:
    results = batch_extract_file_sync([test_files[0]])
    assert len(results) == 1
    assert results[0].content == "Test content 0"


def test_batch_extract_file_sync_multiple(test_files: list[Path]) -> None:
    results = batch_extract_file_sync(test_files)
    assert len(results) == 3
    for i, result in enumerate(results):
        assert result.content == f"Test content {i}"


def test_batch_extract_file_sync_with_error(tmp_path: Path) -> None:
    valid_file = tmp_path / "valid.txt"
    valid_file.write_text("Valid content")

    invalid_file = tmp_path / "nonexistent.txt"

    results = batch_extract_file_sync([valid_file, invalid_file])

    assert len(results) == 2
    assert results[0].content == "Valid content"
    assert "Error:" in results[1].content
    assert results[1].metadata.get("error") is not None


def test_batch_extract_file_sync_with_config(test_files: list[Path]) -> None:
    config = ExtractionConfig(chunk_content=True, max_chars=100)

    with patch("kreuzberg.extraction.extract_file_sync") as mock_extract:
        mock_extract.return_value = ExtractionResult(
            content="Custom result", mime_type="text/plain", metadata={}, chunks=[]
        )

        results = batch_extract_file_sync(test_files, config=config)

        assert len(results) == 3

        for call in mock_extract.call_args_list:
            assert call[1]["config"] == config


def test_batch_extract_bytes_sync_empty() -> None:
    results = batch_extract_bytes_sync([])
    assert results == []


def test_batch_extract_bytes_sync_single(test_bytes: list[tuple[bytes, str]]) -> None:
    results = batch_extract_bytes_sync([test_bytes[0]])
    assert len(results) == 1
    assert "Test content 1" in results[0].content


def test_batch_extract_bytes_sync_multiple(test_bytes: list[tuple[bytes, str]]) -> None:
    results = batch_extract_bytes_sync(test_bytes)
    assert len(results) == 3
    for i, result in enumerate(results):
        assert f"Test content {i + 1}" in result.content


def test_batch_extract_bytes_sync_with_error() -> None:
    with patch("kreuzberg.extraction.extract_bytes_sync") as mock_extract:
        mock_extract.side_effect = [
            ExtractionResult(content="OK", mime_type="text/plain", metadata={}, chunks=[]),
            RuntimeError("Extract failed"),
        ]

        contents = [(b"data1", "text/plain"), (b"data2", "text/plain")]
        results = batch_extract_bytes_sync(contents)

        assert len(results) == 2
        assert results[0].content == "OK"
        assert "Error: RuntimeError: Extract failed" in results[1].content
        assert results[1].metadata.get("error") is not None


def test_batch_extract_file_sync_parallel_processing(test_files: list[Path]) -> None:
    with patch("kreuzberg.extraction.ThreadPoolExecutor") as mock_executor_class:
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor

        mock_futures = []
        for i, _file in enumerate(test_files):
            future = Mock()
            future.result.return_value = (
                i,
                ExtractionResult(content=f"Content {i}", mime_type="text/plain", metadata={}, chunks=[]),
            )
            mock_futures.append(future)

        mock_executor.submit.side_effect = mock_futures

        with patch("kreuzberg.extraction.as_completed", return_value=mock_futures):
            results = batch_extract_file_sync(test_files)

        assert len(results) == 3

        mock_executor_class.assert_called_once()
        assert mock_executor.submit.call_count == 3


def test_batch_extract_bytes_sync_parallel_processing(test_bytes: list[tuple[bytes, str]]) -> None:
    with patch("kreuzberg.extraction.ThreadPoolExecutor") as mock_executor_class:
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor

        mock_futures = []
        for i, (_content, _mime) in enumerate(test_bytes):
            future = Mock()
            future.result.return_value = (
                i,
                ExtractionResult(content=f"Result {i}", mime_type="text/plain", metadata={}, chunks=[]),
            )
            mock_futures.append(future)

        mock_executor.submit.side_effect = mock_futures

        with patch("kreuzberg.extraction.as_completed", return_value=mock_futures):
            results = batch_extract_bytes_sync(test_bytes)

        assert len(results) == 3

        mock_executor_class.assert_called_once()
        assert mock_executor.submit.call_count == 3


@pytest.mark.anyio
async def test_batch_extract_file_preserves_order() -> None:
    file_paths = [Path(f"file{i}") for i in range(5)]

    with patch("kreuzberg.extraction.extract_file") as mock_extract:

        async def extract_with_delay(file_path: Path, config: Any = None, mime_type: Any = None) -> ExtractionResult:
            import anyio

            delay = 0.1 * (5 - int(file_path.name[-1]))
            await anyio.sleep(delay)
            return ExtractionResult(
                content=f"Content from {file_path.name}", mime_type="text/plain", metadata={}, chunks=[]
            )

        mock_extract.side_effect = extract_with_delay

        results = await batch_extract_file(file_paths)

        assert len(results) == 5
        for i, result in enumerate(results):
            assert result.content == f"Content from file{i}"
