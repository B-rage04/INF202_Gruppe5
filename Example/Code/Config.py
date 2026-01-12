from src.LoadTOML import LoadTOML

sysConfig = LoadTOML.loadTomlFile("Exsample/Globalcofig/SysConfig.toml")
print("System Configuration:", sysConfig)
