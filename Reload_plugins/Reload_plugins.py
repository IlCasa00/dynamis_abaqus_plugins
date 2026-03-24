import sys, importlib

def reload_plugins():
    modules_copy = list(sys.modules.items())   # <<< COPIA, non cambia più

    count = 0
    for name, module in modules_copy:

        filename = getattr(module, "__file__", None)
        if not filename:
            continue

        filename = filename.replace("\\", "/").lower()

        # Filtra SOLO plugin (cartelle abaqus_plugins o SIMULIA/CAE/plugins)
        if "abaqus_plugins" in filename or "/plugins/" in filename:
            try:
                importlib.reload(module)
                count += 1
            except Exception as e:
                print("FAILED:", name, "->", e)

    print("Ricaricati", count, "moduli.")
