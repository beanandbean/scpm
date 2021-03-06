import os

_loaded_modules = {}


def _package_root_impl(env, package):
    return env.Dir("$BUILDROOT/$EXTERNALDIR/" + package)


def _package_entry_impl(env, package, entry):
    return env.Entry(os.path.join(env.PackageRoot(package).path, entry))


def _unique_flatten_impl(env, objs):
    # Store unique objects loaded in module
    used = set()
    return list(reversed([obj for obj in reversed(env.Flatten(objs)) if (not obj in used) and (used.add(obj) or True)]))


def _load_impl(env, module, path):
    if not module in _loaded_modules:
        _loaded_modules[module] = []

        build_path = env.PackageRoot(module)
        lib_path = os.path.join(env.Dir(".").srcnode().path, path)
        env.VariantDir(build_path, lib_path, duplicate=False)

        pkgroot = env["PKGROOT"]
        env.Replace(PKGROOT=build_path.abspath)
        objs = env.SConscript(dirs=build_path)
        if objs:
            _loaded_modules[module] = env.UniqueFlatten(objs)

        # Restore original package root
        env.Replace(PKGROOT=pkgroot)
    return _loaded_modules[module]


def _main_program_impl(env, *args, **kwargs):
    program = env.Program(*args, **kwargs)
    env.Default(program)
    env.Clean(program, "$BUILDROOT")
    return program


def _objects_impl(env, files, *args, **kwargs):
    return env.Flatten([env.Object(f, *args, **kwargs) for f in env.Flatten(files)])


def _export_files_impl(env, files, to="."):
    return env.Flatten([env.Install(to, env.File(f).srcnode()) for f in env.Flatten(files)])


def _export_dir_impl(env, directory, target=".", files="*", **kwargs):
    root_dir = env.Dir(directory)
    root_path = root_dir.abspath
    srcroot_path = root_dir.srcnode().abspath
    fs = []
    for f in env.RecGlob(directory, files, **kwargs):
        if os.path.commonpath([f.abspath, root_path]) == root_path:
            relative = os.path.relpath(f.abspath, root_path)
        elif os.path.commonpath([f.abspath, srcroot_path]) == srcroot_path:
            relative = os.path.relpath(f.abspath, srcroot_path)
        else:
            continue
        fs += env.ExportFiles(f, os.path.join(target,
                                              os.path.split(relative)[0]))
    return fs


def _rec_glob_impl(env, directory, files="*", **kwargs):
    dir_obj = env.Dir(directory)
    fs = env.Glob(os.path.join(directory, files), **kwargs)
    for item in env.Glob(os.path.join(directory, "*")):
        if isinstance(item, type(dir_obj)):
            subpath = os.path.join(
                directory, os.path.relpath(item.path, dir_obj.path))
            fs += env.RecGlob(subpath, files)
    return fs


def setup(env):
    env.Export(env=env)

    builtins = ["default", "textfile"]
    for builtin in builtins:
        tool = env.Tool(builtin)
        if tool:
            tool(env)

    env.Replace(ENV=os.environ)
    env.Replace(PKGROOT=env.Dir("#scons_build").abspath)
    env.SetDefault(BUILDROOT="#scons_build", EXTERNALDIR="scons_external")

    env.AddMethod(_package_root_impl, "PackageRoot")
    env.AddMethod(_package_entry_impl, "PackageEntry")

    env.AddMethod(_unique_flatten_impl, "UniqueFlatten")

    env.AddMethod(_load_impl, "Load")
    env.AddMethod(_main_program_impl, "MainProgram")
    env.AddMethod(_objects_impl, "Objects")

    env.AddMethod(_export_files_impl, "ExportFiles")
    env.AddMethod(_export_dir_impl, "ExportDir")
    env.AddMethod(_rec_glob_impl, "RecGlob")

    env.Append(CPPPATH=[env.Dir("$BUILDROOT/$EXTERNALDIR/")])

    env.VariantDir("$BUILDROOT", ".", duplicate=False)
    env.Clean(".", "$BUILDROOT")
