import tomllib as toml

class LoadTOML:
    def load_toml_file(file_path: str) -> dict:
        """
        Loads a TOML file and returns its contents as a dictionary.
        """
        with open(file_path, "rb") as toml_file:
            config = toml.load(toml_file)
        return config