from pathlib import Path

import cv2
import numpy as np


class VideoCreator:

    def __init__(self, imageDir="Output/images/", fps=10):
        self.imageDir = Path(imageDir)
        self.fps = fps

    def create_video_from_run(self, run_number, outputPath=None):
        run_dir = self.imageDir / f"run{run_number}"

        if not run_dir.exists():
            raise FileNotFoundError(f"Run directory {run_dir} does not exist")

        image_files = sorted(
            run_dir.glob("oil_step*.png"), key=lambda x: int(x.stem.split("step")[1])
        )

        if not image_files:
            raise ValueError(f"No images found in {run_dir}")

        if outputPath is None:
            videosDir = self.imageDir.parent / "videos"
            videosDir.mkdir(parents=True, exist_ok=True)
            outputPath = videosDir / f"run{run_number}_video.mp4"
        else:
            outputPath = Path(outputPath)
            outputPath.parent.mkdir(parents=True, exist_ok=True)

        firstImage = cv2.imread(str(image_files[0]))
        height, width, _ = firstImage.shape

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        videoWriter = cv2.VideoWriter(
            str(outputPath), fourcc, self.fps, (width, height)
        )

        for imageFile in image_files:
            frame = cv2.imread(str(imageFile))
            videoWriter.write(frame)

        videoWriter.release()
        return str(outputPath)

    def create_video_from_images(self, imagePattern, outputPath):
        image_files = sorted(self.imageDir.glob(imagePattern))

        if not image_files:
            raise ValueError(f"No images found matching pattern {imagePattern}")

        outputPath = Path(outputPath)
        outputPath.parent.mkdir(parents=True, exist_ok=True)

        first_image = cv2.imread(str(image_files[0]))
        height, width, _ = first_image.shape

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        videoWriter = cv2.VideoWriter(
            str(outputPath), fourcc, self.fps, (width, height)
        )

        for imageFile in image_files:
            frame = cv2.imread(str(imageFile))
            if frame is not None:
                videoWriter.write(frame)

        videoWriter.release()
        return str(outputPath)

    def createComparisonVideo(self, runNumbers, outputPath=None):
        if not runNumbers:
            raise ValueError("At least one run number must be provided")

        allRunImages = []
        maxSteps = 0

        for runNum in runNumbers:
            runDir = self.imageDir / f"run{runNum}"
            if not runDir.exists():
                raise FileNotFoundError(f"Run directory {runDir} does not exist")

            images = sorted(
                runDir.glob("oil_step*.png"),
                key=lambda x: int(x.stem.split("step")[1]),
            )
            allRunImages.append(images)
            maxSteps = max(maxSteps, len(images))

        if outputPath is None:
            outputPath = (
                self.imageDir / f"comparison_runs_{'_'.join(map(str, runNumbers))}.mp4"
            )
        else:
            outputPath = Path(outputPath)
            outputPath.parent.mkdir(parents=True, exist_ok=True)

        firstFrames = [cv2.imread(str(images[0])) for images in allRunImages]
        height, width, _ = firstFrames[0].shape

        numRuns = len(runNumbers)
        cols = min(2, numRuns)
        rows = (numRuns + cols - 1) // cols

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(
            str(outputPath), fourcc, self.fps, (width * cols, height * rows)
        )

        for step in range(maxSteps):
            combinedFrame = np.zeros((height * rows, width * cols, 3), dtype=np.uint8)

            for idx, images in enumerate(allRunImages):
                if step < len(images):
                    frame = cv2.imread(str(images[step]))
                    row = idx // cols
                    col = idx % cols
                    combinedFrame[
                        row * height : (row + 1) * height,
                        col * width : (col + 1) * width,
                    ] = frame

            video_writer.write(combinedFrame)

        video_writer.release()
        return str(outputPath)
