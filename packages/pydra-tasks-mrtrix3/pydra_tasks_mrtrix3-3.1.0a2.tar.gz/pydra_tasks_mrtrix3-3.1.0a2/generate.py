#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import subprocess as sp
import typing as ty
from importlib import import_module
import logging
import tempfile
from traceback import format_exc
import re
from tqdm import tqdm
import click
import black.report
import black.parsing
from fileformats.core import FileSet
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, ImageOut, Tracks
from pydra.compose import shell
from pydra.compose.base import NO_DEFAULT
from pydra.utils.typing import MultiInputObj
from pydra.utils.general import get_fields, add_exc_note


logger = logging.getLogger("pydra-auto-gen")

# Ignore non-standard tools that will need to be added manually
IGNORE = [
    "blend",
    "convert_bruker",
    "gen_scheme",
    "notfound",
    "for_each",
    "mrview",
    "shview",
]


CMD_PREFIXES = [
    "fivett",
    "afd",
    "amp",
    "connectome",
    "dcm",
    "dir",
    "dwi",
    "fixel",
    "fod",
    "label",
    "mask",
    "mesh",
    "mr",
    "mt",
    "peaks",
    "sh",
    "tck",
    "tensor",
    "transform",
    "tsf",
    "voxel",
    "vector",
    "warp",
    "response",
]


XFAIL = [
    "dirsplit",
    "dwi2mask_3dautomask",
    "dwi2mask_ants",
    "dwi2mask_b02template",
    "dwi2mask_consensus",
    "dwi2mask_fslbet",
    "dwi2mask_hdbet",
    "dwi2mask_legacy",
    "dwi2mask_mean",
    "dwi2mask_mtnorm",
    "dwi2mask_synthstrip",
    "dwi2mask_trace",
    "dwi2response_dhollander",
    "dwi2response_fa",
    "dwi2response_manual",
    "dwi2response_msmt_5tt",
    "dwi2response_tax",
    "dwi2response_tournier",
    "dwibiascorrect_ants",
    "dwibiascorrect_fsl",
    "dwibiascorrect_mtnorm",
    "dwibiasnormmask",
    "dwicat",
    "dwifslpreproc",
    "dwigradcheck",
    "dwinormalise_group",
    "dwinormalise_manual",
    "dwinormalise_mtnorm",
    "dwishellmath",
    "fivettgen_freesurfer",
    "fivettgen_fsl",
    "fivettgen_gif",
    "fivettgen_hsvs",
    "fixelcfestats",
    "fixelconnectivity",
    "fixelconvert",
    "fixelcorrespondence",
    "fixelcrop",
    "fixelfilter",
    "fixelreorient",
    "labelsgmfix",
    "mask2glass",
    "mrconvert",
    "mrstats",
    "mrtransform",
    "mrtrix_cleanup",
    "population_template",
    "responsemean",
    "tck2fixel",
    "tckstats",
    "tsfmult",
    "voxel2fixel",
    "warpinvert",
]


@click.command(
    help="""Loops through all MRtrix commands to generate Pydra
(https://pydra.readthedocs.io) task interfaces for them

CMD_DIR the command directory to list the commands from

OUTPUT_DIR the output directory to write the generated files to

MRTRIX_VERSION the version of MRTrix the commands are generated for
"""
)
@click.argument(
    "cmd_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.argument("output_dir", type=click.Path(exists=False, path_type=Path))
@click.argument("mrtrix_version", type=str)
@click.option(
    "--log-errors/--raise-errors",
    type=bool,
    help="whether to log errors (and skip to the next tool) instead of raising them",
)
@click.option(
    "--latest/--not-latest",
    type=bool,
    default=False,
    help="whether to write 'latest' module",
)
@click.option(
    "--log-level",
    type=click.Choice(["debug", "info", "warning", "error", "critical"]),
    default="warning",
    help="logging level",
)
def auto_gen_mrtrix3_pydra(
    cmd_dir: Path,
    mrtrix_version: str,
    output_dir: Path,
    log_errors: bool,
    latest: bool,
    log_level: str,
):

    logging.basicConfig(level=getattr(logging, log_level.upper()))

    pkg_version = "v" + "_".join(mrtrix_version.split(".")[:2])

    cmd_dir = cmd_dir.absolute()

    # Insert output dir to path so we can load the generated tasks in order to
    # generate the tests
    sys.path.insert(0, str(output_dir))

    manual_cmds = []
    manual_path = output_dir / "pydra" / "tasks" / "mrtrix3" / "manual"
    if manual_path.exists():
        for manual_file in manual_path.iterdir():
            manual_cmd = manual_file.stem
            if not manual_cmd.startswith(".") and not manual_cmd.startswith("__"):
                manual_cmds.append(manual_cmd)

    cmds = []
    for cmd_name in tqdm(
        sorted(os.listdir(cmd_dir)),
        "generating Pydra interfaces for all MRtrix3 commands",
    ):
        if (
            cmd_name.startswith("_")
            or "." in cmd_name
            or cmd_name in IGNORE
            or cmd_name in manual_cmds
        ):
            continue
        cmd = [str(cmd_dir / cmd_name)]
        try:
            cmds.extend(
                auto_gen_cmd(
                    cmd, cmd_name, output_dir, cmd_dir, log_errors, pkg_version
                )
            )
        except Exception as e:
            add_exc_note(e, f"when attempting to generate {cmd} in {output_dir}")
            raise e

    # Write init
    init_path = output_dir / "pydra" / "tasks" / "mrtrix3" / pkg_version / "__init__.py"
    imports = "\n".join(f"from .{c} import {pascal_case_task_name(c)}" for c in cmds)
    imports += "\n" + "\n".join(
        f"from ..manual.{c} import {pascal_case_task_name(c)}" for c in manual_cmds
    )
    init_path.write_text(f"# Auto-generated, do not edit\n\n{imports}\n")

    if latest:
        latest_path = output_dir / "pydra" / "tasks" / "mrtrix3" / "latest.py"
        latest_path.write_text(
            f"# Auto-generated, do not edit\n\nfrom .{pkg_version} import *\n"
        )
        print(f"Generated pydra.tasks.mrtrix3.{pkg_version} package")

    # Test out import
    import_module(f"pydra.tasks.mrtrix3.{pkg_version}")


def auto_gen_cmd(
    cmd: ty.List[str],
    cmd_name: str,
    output_dir: Path,
    cmd_dir: Path,
    log_errors: bool,
    pkg_version: str,
) -> ty.List[str]:
    base_cmd = str(cmd_dir / cmd[0])
    cmd = [base_cmd] + cmd[1:]
    try:
        code_str = sp.check_output(cmd + ["__print_pydra_code__"]).decode("utf-8")
    except sp.CalledProcessError:
        if log_errors:
            logger.error("Could not generate interface for '%s'", cmd_name)
            logger.error(format_exc())
            return []
        else:
            raise

    if re.match(r"(\w+,)+\w+", code_str):
        sub_cmds = []
        for algorithm in code_str.split(","):
            sub_cmds.extend(
                auto_gen_cmd(
                    cmd + [algorithm],
                    f"{cmd_name}_{algorithm}",
                    output_dir,
                    cmd_dir,
                    log_errors,
                    pkg_version,
                )
            )
        return sub_cmds

    # Since Python identifiers can't start with numbers we need to rename 5tt*
    # with fivett*
    if cmd_name.startswith("5tt"):
        old_name = cmd_name
        cmd_name = escape_cmd_name(cmd_name)
        code_str = code_str.replace(f"class {old_name}", f"class {cmd_name}")
        code_str = code_str.replace(f"{old_name}_input", f"{cmd_name}_input")
        code_str = code_str.replace(f"{old_name}_output", f"{cmd_name}_output")
        code_str = re.sub(r"(?<!\w)5tt_in(?!\w)", "in_5tt", code_str)
    try:
        try:
            code_str = black.format_file_contents(
                code_str, fast=False, mode=black.FileMode()
            )
        except black.report.NothingChanged:
            pass
        except black.parsing.InvalidInput:
            if log_errors:
                logger.error(
                    "Could not parse generated interface (%s) for '%s'", cmd_name
                )
                logger.error(format_exc())
                return []
            else:
                raise
    except Exception as e:
        tfile = Path(tempfile.mkdtemp()) / (cmd_name + ".py")
        tfile.write_text(code_str)
        e.add_note(f"when formatting {cmd_name}")
        e.add_note(f"generated file is {tfile}")
        raise e
    output_path = (
        output_dir / "pydra" / "tasks" / "mrtrix3" / pkg_version / (cmd_name + ".py")
    )
    output_path.parent.mkdir(exist_ok=True, parents=True)
    with open(output_path, "w") as f:
        f.write(code_str)
    logger.info("%s", cmd_name)
    try:
        auto_gen_test(cmd_name, output_dir, log_errors, pkg_version)
    except Exception:
        if log_errors:
            logger.error("Test generation failed for '%s'", cmd_name)
            logger.error(format_exc())
            return []
        else:
            raise
    return [cmd_name]


def auto_gen_test(cmd_name: str, output_dir: Path, log_errors: bool, pkg_version: str):
    tests_dir = output_dir / "pydra" / "tasks" / "mrtrix3" / pkg_version / "tests"
    tests_dir.mkdir(exist_ok=True)
    module = import_module(f"pydra.tasks.mrtrix3.{pkg_version}.{cmd_name}")
    definition_klass = getattr(module, pascal_case_task_name(cmd_name))

    input_fields = get_fields(definition_klass)
    output_fields = get_fields(definition_klass.Outputs)
    output_fields_dict = {f.name: f for f in output_fields}

    code_str = f"""# Auto-generated test for {cmd_name}

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.{pkg_version} import {pascal_case_task_name(cmd_name)}
"""

    if cmd_name in XFAIL:
        code_str += (
            f"""@pytest.mark.xfail(reason="Job {cmd_name} is known not pass yet")"""
        )

    code_str += f"""
@pytest.mark.xfail
def test_{cmd_name.lower()}(tmp_path, cli_parse_only):

    task = {pascal_case_task_name(cmd_name)}(
"""

    field: shell.arg
    for field in input_fields:
        if field.name in (
            "executable",
            "help",
            "version",
            "quiet",
            "info",
            "nthreads",
            "append_args",
            "config",
            "args",
        ):
            continue

        def get_value(type_):
            if type_ is ImageIn:
                value = "Nifti1.sample()"
            elif type_ is Tracks:
                value = "Tracks.sample()"
            elif type_ is int:
                value = "1"
            elif type_ is float:
                value = "1.0"
            elif type_ is str:
                value = '"a-string"'
            elif type_ is bool:
                value = "True"
            elif type_ is Path:
                try:
                    output_field = output_fields_dict[field.name]
                except AttributeError:
                    pass
                else:
                    output_type = output_field.type
                    if ty.get_origin(output_type) is MultiInputObj:
                        output_type = ty.get_args(output_type)[0]
                    if ty.get_origin(output_type) in (list, tuple):
                        output_type = ty.get_args(output_type)[0]
                    if output_type is ImageOut:
                        output_type = ImageFormat
                value = f"{output_type.__name__}.sample()"
            elif ty.get_origin(type_) is ty.Union:
                value = get_value(ty.get_args(type_)[0])
            elif ty.get_origin(type_) is MultiInputObj:
                value = "[" + get_value(ty.get_args(type_)[0]) + "]"
            elif ty.get_origin(type_) and issubclass(ty.get_origin(type_), ty.Sequence):
                value = (
                    ty.get_origin(type_).__name__
                    + "(["
                    + ", ".join(get_value(a) for a in ty.get_args(type_))
                    + "])"
                )
            elif type_ is ty.Any or issubclass(type_, FileSet):
                value = "File.sample()"
            else:
                raise NotImplementedError
            return value

        if not field.mandatory:
            value = field.default
        elif field.allowed_values:
            value = repr(field.allowed_values[0])
        else:
            value = get_value(field.type)

        code_str += f"        {field.name}={value},\n"

    code_str += """
    )
    result = task(worker="debug")
    assert not result.errored
"""

    try:
        code_str = black.format_file_contents(
            code_str, fast=False, mode=black.FileMode()
        )
    except black.report.NothingChanged:
        pass

    with open(tests_dir / f"test_{cmd_name}.py", "w") as f:
        f.write(code_str)


def escape_cmd_name(cmd_name: str) -> str:
    return cmd_name.replace("5tt", "fivett")


def pascal_case_task_name(cmd_name: str) -> str:
    # convert to PascalCase
    if cmd_name == "population_template":
        return "PopulationTemplate"
    try:
        return "".join(
            g.capitalize()
            for g in re.match(
                rf"({'|'.join(CMD_PREFIXES)}?)(2?)([^_]+)(_?)(.*)", cmd_name
            ).groups()
        )
    except AttributeError as e:
        raise ValueError(
            f"Could not convert {cmd_name} to PascalCase, please add its prefix to CMD_PREFIXES"
        ) from e


if __name__ == "__main__":
    from pathlib import Path

    script_dir = Path(__file__).parent

    mrtrix_version = sp.check_output(
        "git describe --tags --abbrev=0", cwd=script_dir, shell=True
    ).decode("utf-8")

    auto_gen_mrtrix3_pydra(sys.argv[1:])
