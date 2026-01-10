from pathlib import Path

import cv2
import numpy as np


class VideoCreator:

    def __init__(self, image_dir="Output/images/", fps=10):
        self.image_dir = Path(image_dir)
        self.fps = fps

    def create_video_from_run(self, run_number, output_path=None):
        run_dir = self.image_dir / f"run{run_number}"

        if not run_dir.exists():
            raise FileNotFoundError(f"Run directory {run_dir} does not exist")

        image_files = sorted(
            run_dir.glob("oil_step*.png"), key=lambda x: int(x.stem.split("step")[1])
        )

        if not image_files:
            raise ValueError(f"No images found in {run_dir}")

        if output_path is None:
            videos_dir = self.image_dir.parent / "videos"
            videos_dir.mkdir(parents=True, exist_ok=True)
            output_path = videos_dir / f"run{run_number}_video.mp4"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        first_image = cv2.imread(str(image_files[0]))
        height, width, _ = first_image.shape

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(
            str(output_path), fourcc, self.fps, (width, height)
        )

        for image_file in image_files:
            frame = cv2.imread(str(image_file))
            video_writer.write(frame)

        video_writer.release()
        return str(output_path)

    def create_video_from_images(self, image_pattern, output_path):
        image_files = sorted(self.image_dir.glob(image_pattern))

        if not image_files:
            raise ValueError(f"No images found matching pattern {image_pattern}")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        first_image = cv2.imread(str(image_files[0]))
        height, width, _ = first_image.shape

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(
            str(output_path), fourcc, self.fps, (width, height)
        )

        for image_file in image_files:
            frame = cv2.imread(str(image_file))
            if frame is not None:
                video_writer.write(frame)

        video_writer.release()
        return str(output_path)

    def create_comparison_video(self, run_numbers, output_path=None):
        if not run_numbers:
            raise ValueError("At least one run number must be provided")

        all_run_images = []
        max_steps = 0

        for run_num in run_numbers:
            run_dir = self.image_dir / f"run{run_num}"
            if not run_dir.exists():
                raise FileNotFoundError(f"Run directory {run_dir} does not exist")

            images = sorted(
                run_dir.glob("oil_step*.png"),
                key=lambda x: int(x.stem.split("step")[1]),
            )
            all_run_images.append(images)
            max_steps = max(max_steps, len(images))

        if output_path is None:
            output_path = (
                self.image_dir
                / f"comparison_runs_{'_'.join(map(str, run_numbers))}.mp4"
            )
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        first_frames = [cv2.imread(str(images[0])) for images in all_run_images]
        height, width, _ = first_frames[0].shape

        num_runs = len(run_numbers)
        cols = min(2, num_runs)
        rows = (num_runs + cols - 1) // cols

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(
            str(output_path), fourcc, self.fps, (width * cols, height * rows)
        )

        for step in range(max_steps):
            combined_frame = np.zeros((height * rows, width * cols, 3), dtype=np.uint8)

            for idx, images in enumerate(all_run_images):
                if step < len(images):
                    frame = cv2.imread(str(images[step]))
                    row = idx // cols
                    col = idx % cols
                    combined_frame[
                        row * height : (row + 1) * height,
                        col * width : (col + 1) * width,
                    ] = frame

            video_writer.write(combined_frame)

        video_writer.release()
        return str(output_path)
