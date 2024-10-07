from os import listdir
from os.path import isfile, join, isdir

def getAllCogsInFolder(mypath):
    cogs = []

    onlyfolders = [f for f in listdir(mypath) if isdir(join(mypath, f))]
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    for file in onlyfiles:
        if file.split(".")[1] == "py":
            cogs.append(file[:-3])

    for folder in onlyfolders:
        onlyfiles = [f for f in listdir(mypath + f"/{folder}") if isfile(join(mypath + f"/{folder}", f))]
        for file in onlyfiles:
            if file.split(".")[1] == "py":
                cogs.append(file[:-3])
    return cogs

async def loadCog(client, cog, confirm=False):
    try:
        await client.load_extension(cog)
    except Exception as e:
        exc = '{}.{}'.format(type(e).__name__, e)
        print(f'Falha ao carregar o(a) {cog}. Motivo: {exc}')
    else:
        if confirm:
            print(f"{cog} carregado com sucesso!")