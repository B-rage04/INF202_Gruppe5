def configTest():
    from src.IO.config import Config
    from src.IO.LoadTOML import LoadTOML

    configloader = LoadTOML()
    Config = configloader.loadConfigFile("test/utilitiesTests/ConfigTest.toml")
    return Config
