import cv2
import numpy as np
import pytest
from pathlib import Path

from src.video import VideoCreator


def _write_image(path: Path, size=(20, 30), color=(0, 0, 0)):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = np.full((size[0], size[1], 3), color, dtype=np.uint8)
    cv2.imwrite(str(path), img)


def _read_video_meta(video_path: Path):
    cap = cv2.VideoCapture(str(video_path))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return frame_count, width, height


def test_create_video_from_run_creates_file_and_dimensions(tmp_path):
    images_root = tmp_path / "images"
    run_dir = images_root / "run1"
    _write_image(run_dir / "oil_step0.png", size=(12, 16), color=(255, 0, 0))
    _write_image(run_dir / "oil_step1.png", size=(12, 16), color=(0, 255, 0))

    vc = VideoCreator(image_dir=images_root, fps=5)
    out_path = Path(vc.create_video_from_run(1))

    assert out_path.exists()
    frame_count, width, height = _read_video_meta(out_path)
    assert frame_count == 2
    assert width == 16 and height == 12


def test_create_video_from_run_missing_directory(tmp_path):
    vc = VideoCreator(image_dir=tmp_path / "images", fps=5)
    with pytest.raises(FileNotFoundError):
        vc.create_video_from_run(99)


def test_create_video_from_run_no_images(tmp_path):
    images_root = tmp_path / "images"
    run_dir = images_root / "run2"
    run_dir.mkdir(parents=True, exist_ok=True)

    vc = VideoCreator(image_dir=images_root)
    with pytest.raises(ValueError):
        vc.create_video_from_run(2)


def test_create_video_from_images_glob(tmp_path):
    images_root = tmp_path / "images"
    _write_image(images_root / "frame0.png", size=(10, 10), color=(0, 0, 255))
    _write_image(images_root / "frame1.png", size=(10, 10), color=(0, 255, 255))

    vc = VideoCreator(image_dir=images_root, fps=5)
    out_path = tmp_path / "videos" / "glob_video.mp4"
    result = Path(vc.create_video_from_images("*.png", out_path))

    assert result.exists()
    frame_count, width, height = _read_video_meta(result)
    assert frame_count == 2
    assert width == 10 and height == 10


def test_create_comparison_video_combines_runs(tmp_path):
    images_root = tmp_path / "images"
    run1 = images_root / "run1"
    run2 = images_root / "run2"
    _write_image(run1 / "oil_step0.png", size=(8, 8), color=(10, 10, 10))
    _write_image(run1 / "oil_step1.png", size=(8, 8), color=(20, 20, 20))
    _write_image(run2 / "oil_step0.png", size=(8, 8), color=(30, 30, 30))

    vc = VideoCreator(image_dir=images_root, fps=5)
    out_path = vc.create_comparison_video([1, 2])
    out_path = Path(out_path)

    assert out_path.exists()
    frame_count, width, height = _read_video_meta(out_path)
    assert frame_count == 2  # max steps across runs
    assert width == 16 and height == 8  # two runs side-by-side
