import tomllib as toml


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
            for fileName in os.listdir(simConfigPath):
                if fileName.endswith(".toml"):
                    fullPath = os.path.join(simConfigPath, fileName)
                    simConfigs.append(self.loadTomlFile(fullPath))
        else:
            simConfigs.append(self.loadTomlFile(simConfigPath))

        return simConfigs
