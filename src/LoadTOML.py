import tomllib as toml


class LoadTOML:
    def load_toml_file(file_path: str) -> dict:
        """
        Loads a TOML file and returns its contents as a dictionary.
        """
        with open(file_path, "rb") as toml_file:
            config = toml.load(toml_file)
        return config

    def load_sim_configs(sysConfig):
        # if directory load all sim configs in dir if single file load that file

        simConfigs = []
        simConfigPath = sysConfig["settings"]["pathToSimConfig"]
        import os

        if os.path.isdir(simConfigPath):
            for file_name in os.listdir(simConfigPath):
                if file_name.endswith(".toml"):
                    full_path = os.path.join(simConfigPath, file_name)
                    simConfigs.append(LoadTOML.load_toml_file(full_path))
        else:
            simConfigs.append(LoadTOML.load_toml_file(simConfigPath))

        return simConfigs
