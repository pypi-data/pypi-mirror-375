import json
import pprint
import sys
from importlib import import_module
from importlib import util as importlib_util
from pathlib import Path


def localized_vars(orig_vars, slice_path):
    """Update (where possible) any references to build-time variables with the best
    guess of the installed location."""
    # The host's sysconfigdata will include references to build-time variables.
    # Update these to refer to the current known install location.
    orig_prefix = orig_vars["prefix"]
    localized_vars = {}
    for key, value in orig_vars.items():
        final = value
        if isinstance(value, str):
            # Replace any reference to the build installation prefix
            final = final.replace(orig_prefix, str(slice_path))
            # Replace any reference to the build-time Framework location
            final = final.replace("-F .", f"-F {slice_path}")
        localized_vars[key] = final

    return localized_vars


def localize_sysconfigdata(sysconfigdata_path, venv_site_packages):
    """Localize a sysconfigdata python module.

    :param support_path: The platform config that contains the sysconfigdata module to
        localize.
    :param venv_site_packages: The site packages folder where the localized
        sysconfigdata module should be output.
    """
    # Import the sysconfigdata module
    spec = importlib_util.spec_from_file_location(
        sysconfigdata_path.stem, sysconfigdata_path
    )
    if spec is None:
        msg = f"Unable to load spec for {sysconfigdata_path}"
        raise ValueError(msg)
    if spec.loader is None:
        msg = f"Spec for {sysconfigdata_path} does not define a loader"
        raise ValueError(msg)
    sysconfigdata = importlib_util.module_from_spec(spec)
    spec.loader.exec_module(sysconfigdata)

    # Write the updated sysconfigdata module into the cross-platform site.
    slice_path = sysconfigdata_path.parent.parent.parent
    with (venv_site_packages / sysconfigdata_path.name).open("w") as f:
        f.write(f"# Generated from {sysconfigdata_path}\n")
        f.write("build_time_vars = ")
        pprint.pprint(
            localized_vars(sysconfigdata.build_time_vars, slice_path),
            stream=f,
            compact=True,
        )

    return sysconfigdata.build_time_vars


def localize_sysconfig_vars(sysconfig_vars_path, venv_site_packages):
    """Localize a sysconfig_vars.json file.

    :param support_path: The platform config that contains the sysconfigdata module to
        localize.
    :param venv_site_packages: The site-packages folder where the localized
        sysconfig_vars.json file should be output.
    :return: The localized sysconfig
    """
    with sysconfig_vars_path.open("rb") as f:
        build_time_vars = json.load(f)

    prefix = sysconfig_vars_path.parent.parent.parent
    sysconfig_vars = localized_vars(build_time_vars, prefix)

    with (venv_site_packages / sysconfig_vars_path.name).open("w") as f:
        json.dump(sysconfig_vars, f, indent=2)

    return sysconfig_vars


def convert_venv(venv_path: Path, sysconfig_path: Path):
    """Convert a virtual environment into a cross-platform environment.

    :param venv_path: The path to the root of the venv.
    :param sysconfig_path: The path to the sysconfig_vars JSON or sysconfigdata Python
        file for the target platform.
    """
    if not venv_path.exists():
        raise ValueError(f"Virtual environment {venv_path} does not exist.")
    if not (venv_path / "bin/python3").exists():
        raise ValueError(f"{venv_path} does not appear to be a virtual environment.")

    # Update path references in the sysconfigdata to reflect local conditions.
    platlibs = list(venv_path.glob("lib/*/site-packages"))
    if len(platlibs) == 0:
        raise ValueError(f"Couldn't find site packages in {venv_path}")
    elif len(platlibs) > 1:
        raise ValueError(f"Found more than one site packages in {venv_path}")

    venv_site_packages_path = platlibs[0]

    if not sysconfig_path.is_file():
        raise ValueError(f"Could not find sysconfig file {sysconfig_path}")

    match sysconfig_path.suffix:
        case ".json":
            sysconfig_vars_path = sysconfig_path
            _, _, _, abiflags, platform, multiarch = sysconfig_vars_path.stem.split("_")

            sysconfigdata_path = (
                sysconfig_vars_path.parent
                / f"_sysconfigdata_{abiflags}_{platform}_{multiarch}.py"
            )
        case ".py":
            sysconfigdata_path = sysconfig_path
            _, _, abiflags, platform, multiarch = sysconfigdata_path.stem.split("_")

            sysconfig_vars_path = (
                sysconfigdata_path.parent
                / f"_sysconfig_vars_{abiflags}_{platform}_{multiarch}.py"
            )
        case _:
            raise ValueError(
                "Don't know how to process sysconfig data "
                f"of type {sysconfig_path.suffix}"
            )

    # Localize the sysconfig data. sysconfigdata *must* exist; sysconfig_vars
    # will only exist on Python 3.14 or newer.
    sysconfig = localize_sysconfigdata(sysconfigdata_path, venv_site_packages_path)
    if sys.version_info[:2] >= (3, 14):
        localize_sysconfig_vars(sysconfig_vars_path, venv_site_packages_path)

    if sysconfig["VERSION"] != venv_site_packages_path.parts[-2][6:]:
        raise ValueError(
            f"target venv is Python {venv_site_packages_path.parts[-2][6:]}; "
            f"sysconfig file is for Python {sysconfig['VERSION']}"
        )

    # Generate the context for the templated cross-target file
    arch, sdk = multiarch.split("-", 1)
    context = {
        "platform": platform,
        "os": platform,  # some platforms use different capitalization here
        "multiarch": multiarch,
        "abiflags": abiflags,
        "arch": arch,
        "sdk": sdk,
    }

    try:
        platform_module = import_module(f"xvenv.platforms.{platform}")
        platform_module.extend_context(context, sysconfig)
    except ImportError:
        raise ValueError(
            f"Don't know how to build a cross-venv file for {platform}"
        ) from None

    cross_multiarch = f"_cross_{platform}_{multiarch.replace('-', '_')}"

    # Render the template for the cross-target file.
    template = (Path(__file__).parent / "_cross_target.py.tmpl").read_text()
    rendered = template.format(**context)
    (venv_site_packages_path / f"{cross_multiarch}.py").write_text(rendered)

    # Write the .pth file that will enable the cross-target modifications
    (venv_site_packages_path / "_cross_venv.pth").write_text(
        f"import {cross_multiarch}\n"
    )

    return f"{context['os']} {multiarch}"
