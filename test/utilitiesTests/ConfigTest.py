def configTest():
    from src.config import Config
    from src.LoadTOML import LoadTOML
    configloader = LoadTOML()
    Config = configloader.loadConfigFile("test/utilitiesTests/ConfigTest.toml")
    return Config