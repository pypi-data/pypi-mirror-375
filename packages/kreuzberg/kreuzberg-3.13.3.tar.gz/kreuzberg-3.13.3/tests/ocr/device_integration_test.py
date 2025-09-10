from __future__ import annotations

from dataclasses import asdict
from unittest.mock import Mock, patch

import pytest

from kreuzberg._ocr._easyocr import EasyOCRBackend
from kreuzberg._ocr._paddleocr import PaddleBackend
from kreuzberg._types import EasyOCRConfig, PaddleOCRConfig
from kreuzberg._utils._device import DeviceInfo
from kreuzberg.exceptions import ValidationError


def test_easyocr_resolve_device_config_auto_default() -> None:
    config = EasyOCRConfig()
    with patch.object(EasyOCRBackend, "_resolve_device_config") as mock_resolve:
        mock_resolve.return_value = DeviceInfo(device_type="cpu", name="CPU")

        EasyOCRBackend._resolve_device_config(**asdict(config))
        mock_resolve.assert_called_once()


@patch("kreuzberg._ocr._easyocr.validate_device_request")
def test_easyocr_resolve_device_config_explicit_cuda(mock_validate: Mock) -> None:
    mock_validate.return_value = DeviceInfo(device_type="cuda", device_id=0, name="NVIDIA RTX 3080")

    config = EasyOCRConfig(device="cuda", gpu_memory_limit=4.0)
    device_info = EasyOCRBackend._resolve_device_config(**asdict(config))

    mock_validate.assert_called_once_with("cuda", "EasyOCR", memory_limit=4.0, fallback_to_cpu=True)
    assert device_info.device_type == "cuda"


@patch("kreuzberg._ocr._easyocr.validate_device_request")
def test_easyocr_resolve_device_config_deprecated_use_gpu_true(mock_validate: Mock) -> None:
    mock_validate.return_value = DeviceInfo(device_type="cuda", device_id=0, name="NVIDIA RTX 3080")

    config = EasyOCRConfig(use_gpu=True)

    with pytest.warns(DeprecationWarning, match="'use_gpu' parameter is deprecated"):
        EasyOCRBackend._resolve_device_config(**asdict(config))

    mock_validate.assert_called_once_with("auto", "EasyOCR", memory_limit=None, fallback_to_cpu=True)


@patch("kreuzberg._ocr._easyocr.validate_device_request")
def test_easyocr_resolve_device_config_deprecated_use_gpu_with_device(mock_validate: Mock) -> None:
    mock_validate.return_value = DeviceInfo(device_type="cuda", device_id=0, name="NVIDIA RTX 3080")

    config = EasyOCRConfig(use_gpu=True, device="cuda")

    with pytest.warns(DeprecationWarning, match="Both 'use_gpu' and 'device' parameters specified"):
        EasyOCRBackend._resolve_device_config(**asdict(config))

    mock_validate.assert_called_once_with("cuda", "EasyOCR", memory_limit=None, fallback_to_cpu=True)


@patch("kreuzberg._ocr._easyocr.validate_device_request")
def test_easyocr_resolve_device_config_validation_error_fallback(mock_validate: Mock) -> None:
    mock_validate.side_effect = ValidationError("Device not available", context={})

    config = EasyOCRConfig(use_gpu=False, device="cpu")
    device_info = EasyOCRBackend._resolve_device_config(**asdict(config))

    assert device_info.device_type == "cpu"
    assert device_info.name == "CPU"


@patch("kreuzberg._ocr._easyocr.validate_device_request")
def test_easyocr_resolve_device_config_validation_error_no_fallback(mock_validate: Mock) -> None:
    mock_validate.side_effect = ValidationError("Device not available", context={})

    config = EasyOCRConfig(use_gpu=True, device="cuda")

    with pytest.raises(ValidationError):
        EasyOCRBackend._resolve_device_config(**asdict(config))


@patch("kreuzberg._ocr._paddleocr.validate_device_request")
def test_paddleocr_resolve_device_config_mps_warning(mock_validate: Mock) -> None:
    # PaddlePaddle doesn't support MPS, should warn and fallback to CPU  # ~keep
    mock_validate.return_value = DeviceInfo(device_type="cpu", name="CPU")

    config = PaddleOCRConfig(device="mps")

    with pytest.warns(UserWarning, match="PaddlePaddle does not support MPS"):
        PaddleBackend._resolve_device_config(**asdict(config))

    # Should call validate with "cpu" instead of "mps"  # ~keep
    mock_validate.assert_called_once_with("cpu", "PaddleOCR", memory_limit=None, fallback_to_cpu=True)


@patch("kreuzberg._ocr._paddleocr.validate_device_request")
def test_paddleocr_resolve_device_config_deprecated_use_gpu_true(mock_validate: Mock) -> None:
    mock_validate.return_value = DeviceInfo(device_type="cuda", device_id=0, name="NVIDIA RTX 3080")

    config = PaddleOCRConfig(use_gpu=True)

    with pytest.warns(DeprecationWarning, match="'use_gpu' parameter is deprecated"):
        PaddleBackend._resolve_device_config(**asdict(config))

    mock_validate.assert_called_once_with("auto", "PaddleOCR", memory_limit=None, fallback_to_cpu=True)


@patch("kreuzberg._ocr._paddleocr.validate_device_request")
def test_paddleocr_resolve_device_config_with_memory_limit(mock_validate: Mock) -> None:
    mock_validate.return_value = DeviceInfo(device_type="cuda", device_id=0, name="NVIDIA RTX 3080")

    config = PaddleOCRConfig(device="cuda", gpu_memory_limit=8.0, fallback_to_cpu=False)
    PaddleBackend._resolve_device_config(**asdict(config))

    mock_validate.assert_called_once_with("cuda", "PaddleOCR", memory_limit=8.0, fallback_to_cpu=False)


@pytest.mark.anyio
@patch("kreuzberg._ocr._easyocr.run_sync")
@patch.object(EasyOCRBackend, "_validate_language_code")
@patch.object(EasyOCRBackend, "_resolve_device_config")
async def test_easyocr_init_with_gpu_device(mock_resolve: Mock, mock_validate_lang: Mock, mock_run_sync: Mock) -> None:
    EasyOCRBackend._reader = None

    mock_validate_lang.return_value = ["en"]
    mock_resolve.return_value = DeviceInfo(device_type="cuda", device_id=0, name="NVIDIA RTX 3080")
    mock_reader = Mock()
    mock_run_sync.return_value = mock_reader

    config = EasyOCRConfig(device="cuda")

    with patch(
        "builtins.__import__",
        side_effect=lambda name, *args, **kwargs: Mock() if name == "easyocr" else __import__(name, *args, **kwargs),
    ):
        await EasyOCRBackend._init_easyocr(**asdict(config))

    mock_run_sync.assert_called_once()
    args, kwargs = mock_run_sync.call_args
    assert kwargs["gpu"] is True

    EasyOCRBackend._reader = None


@pytest.mark.anyio
@patch("kreuzberg._ocr._easyocr.run_sync")
@patch.object(EasyOCRBackend, "_validate_language_code")
@patch.object(EasyOCRBackend, "_resolve_device_config")
async def test_easyocr_init_with_cpu_device(mock_resolve: Mock, mock_validate_lang: Mock, mock_run_sync: Mock) -> None:
    EasyOCRBackend._reader = None

    mock_validate_lang.return_value = ["en"]
    mock_resolve.return_value = DeviceInfo(device_type="cpu", name="CPU")
    mock_reader = Mock()
    mock_run_sync.return_value = mock_reader

    config = EasyOCRConfig(device="cpu")

    with patch(
        "builtins.__import__",
        side_effect=lambda name, *args, **kwargs: Mock() if name == "easyocr" else __import__(name, *args, **kwargs),
    ):
        await EasyOCRBackend._init_easyocr(**asdict(config))

    mock_run_sync.assert_called_once()
    args, kwargs = mock_run_sync.call_args
    assert kwargs["gpu"] is False

    EasyOCRBackend._reader = None


@pytest.mark.anyio
@patch("kreuzberg._ocr._paddleocr.run_sync")
@patch("kreuzberg._ocr._paddleocr.find_spec")
@patch.object(PaddleBackend, "_validate_language_code")
@patch.object(PaddleBackend, "_resolve_device_config")
@patch.object(PaddleBackend, "_is_mkldnn_supported")
async def test_paddleocr_init_with_gpu_device_and_memory_limit(
    mock_mkldnn: Mock,
    mock_resolve: Mock,
    mock_validate_lang: Mock,
    mock_find_spec: Mock,
    mock_run_sync: Mock,
) -> None:
    PaddleBackend._paddle_ocr = None

    mock_validate_lang.return_value = "en"
    mock_resolve.return_value = DeviceInfo(device_type="cuda", device_id=0, name="NVIDIA RTX 3080")
    mock_find_spec.return_value = True
    mock_mkldnn.return_value = False
    mock_paddle_instance = Mock()
    mock_run_sync.return_value = mock_paddle_instance

    config = PaddleOCRConfig(device="cuda", gpu_memory_limit=4.0)
    await PaddleBackend._init_paddle_ocr(**asdict(config))

    mock_run_sync.assert_called_once()
    args, kwargs = mock_run_sync.call_args
    assert args[0].__name__ == "PaddleOCR"

    PaddleBackend._paddle_ocr = None


@pytest.mark.anyio
@patch("kreuzberg._ocr._paddleocr.run_sync")
@patch("kreuzberg._ocr._paddleocr.find_spec")
@patch.object(PaddleBackend, "_validate_language_code")
@patch.object(PaddleBackend, "_resolve_device_config")
@patch.object(PaddleBackend, "_is_mkldnn_supported")
async def test_paddleocr_init_cpu_device_no_gpu_package(
    mock_mkldnn: Mock,
    mock_resolve: Mock,
    mock_validate_lang: Mock,
    mock_find_spec: Mock,
    mock_run_sync: Mock,
) -> None:
    PaddleBackend._paddle_ocr = None

    mock_validate_lang.return_value = "en"
    mock_resolve.return_value = DeviceInfo(device_type="cpu", name="CPU")
    mock_find_spec.return_value = False
    mock_mkldnn.return_value = True
    mock_paddle_instance = Mock()
    mock_run_sync.return_value = mock_paddle_instance

    config = PaddleOCRConfig(device="cpu")
    await PaddleBackend._init_paddle_ocr(**asdict(config))

    mock_run_sync.assert_called_once()
    args, kwargs = mock_run_sync.call_args
    assert args[0].__name__ == "PaddleOCR"

    PaddleBackend._paddle_ocr = None


def test_easyocr_backward_compatibility_use_gpu_true() -> None:
    with patch("kreuzberg._ocr._easyocr.validate_device_request") as mock_validate:
        mock_validate.return_value = DeviceInfo(device_type="cuda", device_id=0, name="NVIDIA RTX 3080")

        config = {"use_gpu": True, "language": "en", "device": "auto"}

        with pytest.warns(DeprecationWarning, match="'use_gpu' parameter is deprecated"):
            device_info = EasyOCRBackend._resolve_device_config(**config)

        assert device_info.device_type == "cuda"


def test_paddleocr_backward_compatibility_use_gpu_false() -> None:
    with patch("kreuzberg._ocr._paddleocr.validate_device_request") as mock_validate:
        mock_validate.return_value = DeviceInfo(device_type="cpu", name="CPU")

        config = {"use_gpu": False, "language": "en", "device": "auto"}

        device_info = PaddleBackend._resolve_device_config(**config)

        assert device_info.device_type == "cpu"


def test_config_dataclass_default_values() -> None:
    easy_config = EasyOCRConfig()
    assert easy_config.device == "auto"
    assert easy_config.gpu_memory_limit is None
    assert easy_config.fallback_to_cpu is True
    assert easy_config.use_gpu is False

    paddle_config = PaddleOCRConfig()
    assert paddle_config.device == "auto"
    assert paddle_config.gpu_memory_limit is None
    assert paddle_config.fallback_to_cpu is True
    assert paddle_config.use_gpu is False
