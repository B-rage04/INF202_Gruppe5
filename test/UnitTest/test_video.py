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
