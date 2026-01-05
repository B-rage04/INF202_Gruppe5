import meshio

msh = meshio.read("bay.msh")

print(msh.points)