import time
import tomllib as toml

from tqdm import tqdm


class LoadTOML:
    def loadTomlFile(
        self, filePath
    ) -> (
        dict
    ):  # TODO: test valid and invalid paths, test valid and invalid toml content
        """
        Loads a TOML file and returns its contents as a dictionary.
        """
        with open(filePath, "rb") as tomlFile:
            config = toml.load(tomlFile)
        return config

    def loadSimConfigs(
        self, sysConfig
    ) -> list[dict]:  # TODO: test with single file and directory
        """ """

        # if directory load all sim configs in dir if single file load that file

        simConfigs = []
        simConfigPath = sysConfig["settings"]["pathToSimConfig"]
        import os

        if os.path.isdir(simConfigPath):
            files = [f for f in os.listdir(simConfigPath) if f.endswith(".toml")]
            start_time = time.perf_counter()
            for fileName in tqdm(
                files,
                desc="Loading configuration files",
                unit="file",
                colour="magenta",
                ncols=100,
                ascii="-#",
            ):
                fullPath = os.path.join(simConfigPath, fileName)
                simConfigs.append(self.loadTomlFile(fullPath))
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            print(f"Loading configuration files completed in {elapsed_ms:.2f} ms")
        else:
            simConfigs.append(self.loadTomlFile(simConfigPath))

        return simConfigs
