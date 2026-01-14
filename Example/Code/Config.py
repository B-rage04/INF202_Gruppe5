from src.LoadTOML import LoadTOML

sysConfig = LoadTOML.loadTomlFile("Example/Globalcofig/SysConfig.toml")
print("System Configuration:", sysConfig)
