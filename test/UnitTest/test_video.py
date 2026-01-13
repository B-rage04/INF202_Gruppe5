import pytest

from src.video import VideoCreator




def test_vid_init(tmp_path):
    vidcre = VideoCreator(tmp_path)
    assert vidcre.image_dir == tmp_path
    assert vidcre.fps == 10


def test_vid_create_nodir():
    vidcre = VideoCreator("fake/this/is/not/here")
    with pytest.raises(FileNotFoundError):
        vidcre.create_video_from_run(4)


def test_vid_create_noimg(tmp_path):
    image_dir = tmp_path / "images"
    run_dir = image_dir / "run1"
    run_dir.mkdir(parents=True)
    vidcre = VideoCreator(image_dir=image_dir)

    with pytest.raises(ValueError):
        vidcre.create_video_from_run(1)

def test_no_outputpath(tmp_path):
    image_dir = tmp_path / "images"
    run_dir = image_dir / "run1"
    run_dir.mkdir(parents=True)
    vidcre = VideoCreator(image_dir)
    