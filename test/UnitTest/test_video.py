import types
from pathlib import Path

import numpy as np
import pytest

from src.IO import video as video_mod


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def make_fake_cv2(tmp_path, imread_map=None):
    """
    Create a minimal fake cv2 module that:
    - reads images
    - writes a fake video file
    """

    class FakeWriter:
        def __init__(self, path, fourcc, fps, size):
            self.path = path
            self.frames = []

        def write(self, frame):
            self.frames.append(frame)

        def release(self):
            Path(self.path).write_bytes(b"FAKE_VIDEO")

    def imread(path):
        path = str(path)
        if imread_map and path in imread_map:
            return imread_map[path]
        return np.zeros((10, 20, 3), dtype=np.uint8)

    fake = types.SimpleNamespace()
    fake.imread = imread
    fake.VideoWriter = FakeWriter
    fake.VideoWriter_fourcc = lambda *args: 0
    return fake


def make_run(image_dir: Path, run: int, n_images=3):
    run_dir = image_dir / f"run{run}"
    run_dir.mkdir(parents=True)
    for i in range(1, n_images + 1):
        (run_dir / f"oilStep{i}.png").write_bytes(b"")


# ---------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------

def test_video_creator_init(tmp_path):
    vc = video_mod.VideoCreator(image_dir=str(tmp_path), fps=12)
    assert vc.image_dir == tmp_path
    assert vc.fps == 12


def test_legacy_imageDir_argument(tmp_path):
    vc = video_mod.VideoCreator(imageDir=str(tmp_path))
    assert vc.imageDir == tmp_path


# ---------------------------------------------------------------------
# createVideoFromRun – error paths
# ---------------------------------------------------------------------

def test_create_video_from_run_missing_dir():
    vc = video_mod.VideoCreator(image_dir="does/not/exist")
    with pytest.raises(FileNotFoundError):
        vc.createVideoFromRun(0)


def test_create_video_from_run_no_images(tmp_path):
    image_dir = tmp_path / "images"
    (image_dir / "run0").mkdir(parents=True)

    vc = video_mod.VideoCreator(image_dir=str(image_dir))
    with pytest.raises(ValueError):
        vc.createVideoFromRun(0)


def test_create_video_from_run_cv2_missing(monkeypatch, tmp_path):
    image_dir = tmp_path / "images"
    make_run(image_dir, run=0, n_images=1)

    monkeypatch.setattr(video_mod, "cv2", None)

    vc = video_mod.VideoCreator(image_dir=str(image_dir))
    with pytest.raises(ImportError):
        vc.createVideoFromRun(0)


# ---------------------------------------------------------------------
# createVideoFromRun – success path
# ---------------------------------------------------------------------

def test_create_video_from_run_success(monkeypatch, tmp_path):
    image_dir = tmp_path / "images"
    make_run(image_dir, run=3, n_images=3)

    fake_cv2 = make_fake_cv2(tmp_path)
    monkeypatch.setattr(video_mod, "cv2", fake_cv2)

    vc = video_mod.VideoCreator(image_dir=str(image_dir), fps=5)
    out = vc.createVideoFromRun(3)

    assert isinstance(out, str)
    assert out.endswith("run3_video.mp4")
    assert Path(out).exists()


def test_create_video_from_run_custom_output(monkeypatch, tmp_path):
    image_dir = tmp_path / "images"
    make_run(image_dir, run=1, n_images=1)

    fake_cv2 = make_fake_cv2(tmp_path)
    monkeypatch.setattr(video_mod, "cv2", fake_cv2)

    outp = tmp_path / "custom" / "vid.mp4"
    vc = video_mod.VideoCreator(image_dir=str(image_dir))
    res = vc.createVideoFromRun(1, outputPath=str(outp))

    assert res == str(outp)
    assert outp.exists()


# ---------------------------------------------------------------------
# createVideoFromImages
# ---------------------------------------------------------------------

def test_create_video_from_images_success(monkeypatch, tmp_path):
    image_dir = tmp_path / "imgs"
    image_dir.mkdir()
    (image_dir / "a.png").write_bytes(b"")
    (image_dir / "b.png").write_bytes(b"")

    fake_cv2 = make_fake_cv2(tmp_path)
    monkeypatch.setattr(video_mod, "cv2", fake_cv2)

    outp = tmp_path / "out.mp4"
    vc = video_mod.VideoCreator(image_dir=str(image_dir))
    res = vc.createVideoFromImages("*.png", str(outp))

    assert res == str(outp)
    assert outp.exists()


def test_create_video_from_images_skips_none_frames(monkeypatch, tmp_path):
    image_dir = tmp_path / "imgs"
    image_dir.mkdir()

    a = image_dir / "a.png"
    b = image_dir / "b.png"
    a.write_bytes(b"")
    b.write_bytes(b"")

    imread_map = {
        str(a): np.zeros((5, 5, 3), dtype=np.uint8),
        str(b): None,
    }

    fake_cv2 = make_fake_cv2(tmp_path, imread_map)
    monkeypatch.setattr(video_mod, "cv2", fake_cv2)

    outp = tmp_path / "out.mp4"
    vc = video_mod.VideoCreator(image_dir=str(image_dir))
    res = vc.createVideoFromImages("*.png", str(outp))

    assert outp.exists()


def test_create_video_from_images_no_images():
    vc = video_mod.VideoCreator(image_dir="missing")
    with pytest.raises(ValueError):
        vc.createVideoFromImages("*.png", "out.mp4")


# ---------------------------------------------------------------------
# createComparisonVideo
# ---------------------------------------------------------------------

def test_create_comparison_video_success(monkeypatch, tmp_path):
    image_dir = tmp_path / "images"
    make_run(image_dir, 0, 1)
    make_run(image_dir, 1, 1)

    fake_cv2 = make_fake_cv2(tmp_path)
    monkeypatch.setattr(video_mod, "cv2", fake_cv2)

    vc = video_mod.VideoCreator(image_dir=str(image_dir))
    out = vc.createComparisonVideo([0, 1])

    assert out.endswith("comparison_runs_0_1.mp4")
    assert Path(out).exists()


def test_create_comparison_video_errors():
    vc = video_mod.VideoCreator(image_dir=".")
    with pytest.raises(ValueError):
        vc.createComparisonVideo([])


def test_create_comparison_video_missing_run(monkeypatch, tmp_path):
    fake_cv2 = make_fake_cv2(tmp_path)
    monkeypatch.setattr(video_mod, "cv2", fake_cv2)

    vc = video_mod.VideoCreator(image_dir=str(tmp_path))
    with pytest.raises(FileNotFoundError):
        vc.createComparisonVideo([0])


# ---------------------------------------------------------------------
# Snake_case wrappers (coverage only)
# ---------------------------------------------------------------------

def test_snake_case_wrappers(monkeypatch, tmp_path):
    image_dir = tmp_path / "images"
    make_run(image_dir, 0, 1)

    fake_cv2 = make_fake_cv2(tmp_path)
    monkeypatch.setattr(video_mod, "cv2", fake_cv2)

    vc = video_mod.VideoCreator(image_dir=str(image_dir))

    assert isinstance(vc.create_video_from_run(0), str)

    (image_dir / "x.png").write_bytes(b"")
    outp = tmp_path / "out.mp4"
    assert vc.create_video_from_images("*.png", str(outp)) == str(outp)

    comp = vc.create_comparison_video([0], outputPath=str(tmp_path / "c.mp4"))
    assert comp.endswith("c.mp4")
