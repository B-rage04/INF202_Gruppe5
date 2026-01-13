import tomllib as toml
from tqdm import tqdm


class LoadTOML:
    def loadTomlFile(self, filePath) -> dict:
        """
        Loads a TOML file and returns its contents as a dictionary.
        """
        with open(filePath, "rb") as tomlFile:
            config = toml.load(tomlFile)
        return config

    def loadSimConfigs(self, sysConfig) -> list[dict]:
        """ """

        # if directory load all sim configs in dir if single file load that file

        simConfigs = []
        simConfigPath = sysConfig["settings"]["pathToSimConfig"]
        import os

        if os.path.isdir(simConfigPath):
            files = [f for f in os.listdir(simConfigPath) if f.endswith(".toml")]
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
        else:
            simConfigs.append(self.loadTomlFile(simConfigPath))

        return simConfigs
