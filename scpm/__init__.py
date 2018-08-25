import os

_loaded_modules = {}


def _module_root_impl(env, module):
    return env.Dir("$BUILDROOT/$EXTERNALDIR/" + module)


def _module_entry_impl(env, module, entry):
    return env.Entry(os.path.join(env.ModuleRoot(module).path, entry))


def _load_impl(env, module, path):
    if not module in _loaded_modules:
        _loaded_modules[module] = []

        build_path = env.ModuleRoot(module)
        lib_path = os.path.join(env.Dir(".").srcnode().path, path)
        env.VariantDir(build_path, lib_path, duplicate=False)

        pkgroot = env["PKGROOT"]
        env.Replace(PKGROOT=build_path.abspath)
        objs = env.SConscript(dirs=build_path)
        if objs:
            # Store unique objects loaded in module
            used = set()
            _loaded_modules[module] = [obj for obj in env.Flatten(
                objs) if (not obj in used) and (used.add(obj) or True)]

        # Restore original package root
        env.Replace(PKGROOT=pkgroot)
    return _loaded_modules[module]


def _objects_impl(env, files, *args, **kwargs):
    return env.Flatten([env.Object(f, *args, **kwargs) for f in env.Flatten(files)])


def _export_files_impl(env, files, to="."):
    return env.Flatten([env.Install(to, env.File(f).srcnode()) for f in env.Flatten(files)])


def setup(env):
    env.Export(env=env)

    builtins = ["default", "textfile"]
    for builtin in builtins:
        tool = env.Tool(builtin)
        if tool:
            tool(env)

    env.Replace(ENV=os.environ)
    env.Replace(PKGROOT=env.Dir("#scons_build").abspath)
    if not "BUILDROOT" in env:
        env.Replace(BUILDROOT="#scons_build")
    if not "EXTERNALDIR" in env:
        env.Replace(EXTERNALDIR="scons_external")

    env.AddMethod(_module_root_impl, "ModuleRoot")
    env.AddMethod(_module_entry_impl, "ModuleEntry")

    env.AddMethod(_load_impl, "Load")
    env.AddMethod(_objects_impl, "Objects")
    env.AddMethod(_export_files_impl, "ExportFiles")

    env.Append(CPPPATH=[env.Dir("$BUILDROOT/$EXTERNALDIR/")])

    env.VariantDir("$BUILDROOT", ".", duplicate=False)
    env.Clean(".", "$BUILDROOT")
