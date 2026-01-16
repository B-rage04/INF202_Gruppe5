import time
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm


class VideoCreator:
    """
    Class for videocreator that returns a video in MP4 format
    This class compiles multiple PNGs into one MP4 video
    """

    def __init__(self, imageDir="Output/images/", fps=10, **kwargs):
        """
        Docstring for initializes te videoCreatorobject
        
        :param imageDir: string path to directory where video should be saved
        :param fps: frames per second
        """


        self.image_dir = Path(imageDir)
        self.imageDir = self.image_dir
        self.fps = fps

    def createVideoFromRun(self, runNumber, outputPath=None):
        """
        Function that compiles all frames from specified simulation into a video
        
        :param runNumber: index for which images to compile to video
        :param outputPath: string for outputpath
        :return: outputPath
        """
        runDir = self.imageDir / f"run{runNumber}"

        if not runDir.exists():
            raise FileNotFoundError(f"Run directory {runDir} does not exist")

        image_files = sorted(
            runDir.glob("oilStep*.png"), key=lambda x: int(x.stem.split("Step")[1])
        )

        if not image_files:
            raise ValueError(f"No images found in {runDir}")

        if outputPath is None:
            videosDir = self.imageDir.parent / "videos"
            videosDir.mkdir(parents=True, exist_ok=True)
            outputPath = videosDir / f"run{runNumber}_video.mp4"
        else:
            outputPath = Path(outputPath)
            outputPath.parent.mkdir(parents=True, exist_ok=True)

        firstImage = cv2.imread(str(image_files[0]))
        height, width, _ = firstImage.shape

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        videoWriter = cv2.VideoWriter(
            str(outputPath), fourcc, self.fps, (width, height)
        )

        start_time = time.perf_counter()
        for imageFile in tqdm(
            image_files,
            desc="Encoding video frames",
            unit="frame",
            colour="blue",
            ncols=100,
            ascii="-#",
        ):
            frame = cv2.imread(str(imageFile))
            videoWriter.write(frame)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        print(f"Video encoding completed in {elapsed_ms:.2f} ms")

        videoWriter.release()
        return str(outputPath)

    def createVideoFromImages(self, imagePattern, outputPath):
        """
        Method that creates a video from glob pattern of images
        
        :param imagePattern: glob pattern of images, ex ("oilStep*.png)
        :param outputPath: destination for videofile
        :return: outputPath as string
        """
        imageFiles = sorted(self.imageDir.glob(imagePattern))

        if not imageFiles:
            raise ValueError(f"No images found matching pattern {imagePattern}")

        outputPath = Path(outputPath)
        outputPath.parent.mkdir(parents=True, exist_ok=True)

        firstImage = cv2.imread(str(imageFiles[0]))
        height, width, _ = firstImage.shape

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        videoWriter = cv2.VideoWriter(
            str(outputPath), fourcc, self.fps, (width, height)
        )

        start_time = time.perf_counter()
        for imageFile in tqdm(
            imageFiles,
            desc="Processing image sequence",
            unit="img",
            colour="cyan",
            ncols=100,
            ascii="-#",
        ):
            frame = cv2.imread(str(imageFile))
            if frame is not None:
                videoWriter.write(frame)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        print(f"Image sequence processing completed in {elapsed_ms:.2f} ms")

        videoWriter.release()
        return str(outputPath)

    def createComparisonVideo(self, runNumbers, outputPath=None):
        """
        takes in multiple runs to compare them
        
        :param runNumbers: a list of numbers for runs to compare (at least 1 is needed to run this function)
        :param outputPath: string of path to save the result of comparison
        :return: outputPath as a string
        """
        if not runNumbers:
            raise ValueError("At least one run number must be provided")

        allRunImages = []
        maxSteps = 0

        start_time = time.perf_counter()
        for runNum in tqdm(
            runNumbers,
            desc="Loading simulation runs",
            unit="run",
            colour="magenta",
            ncols=100,
            ascii="-#",
        ):
            runDir = self.imageDir / f"run{runNum}"
            if not runDir.exists():
                raise FileNotFoundError(f"Run directory {runDir} does not exist")

            images = sorted(
                runDir.glob("oilStep*.png"),
                key=lambda x: int(x.stem.split("Step")[1]),
            )
            allRunImages.append(images)
            maxSteps = max(maxSteps, len(images))
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        print(f"Loading simulation runs completed in {elapsed_ms:.2f} ms")

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
        videoWriter = cv2.VideoWriter(
            str(outputPath), fourcc, self.fps, (width * cols, height * rows)
        )

        start_time = time.perf_counter()
        for step in tqdm(
            range(maxSteps),
            desc="Compositing comparison frames",
            unit="frame",
            colour="green",
            ncols=100,
            ascii="-#",
        ):
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

            videoWriter.write(combinedFrame)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        print(f"Compositing comparison frames completed in {elapsed_ms:.2f} ms")

        videoWriter.release()
        return str(outputPath)
