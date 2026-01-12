import tomllib as toml


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
            for fileName in os.listdir(simConfigPath):
                if fileName.endswith(".toml"):
                    fullPath = os.path.join(simConfigPath, fileName)
                    simConfigs.append(self.loadTomlFile(fullPath))
        else:
            simConfigs.append(self.loadTomlFile(simConfigPath))

        return simConfigs
