class ConfigTest:
    def __init__(self):
        pass
    def __call__(self):
        from src.config import Config
        from src.LoadTOML import LoadTOML
        configloader = LoadTOML()
        Config = configloader.loadConfigFile("test/utilitiesTests/ConfigTest.toml")
        return Config