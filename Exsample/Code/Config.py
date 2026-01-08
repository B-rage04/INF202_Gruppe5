from src.LoadTOML import LoadTOML

sysConfig = LoadTOML.load_toml_file("Exsample/Globalcofig/SysConfig.toml")
print("System Configuration:", sysConfig)
