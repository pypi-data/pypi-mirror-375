from operator import mul
from functools import reduce
import random
import pytest
from pydra2app.xnat import XnatCommand
from conftest import TEST_XNAT_DATASET_BLUEPRINTS, access_dataset


@pytest.mark.parametrize("access_method", ["api", "cs", "cs-internal"])
def test_command_execute(
    xnat_repository, command_spec, work_dir, run_prefix, access_method, xnat_archive_dir
):
    # Get CLI name for dataset (i.e. file system path prepended by 'file_system//')

    duplicates = 1
    bp = TEST_XNAT_DATASET_BLUEPRINTS["concatenate_test"]
    project_id = (
        run_prefix
        + "contenatecommand"
        + access_method
        + str(hex(random.getrandbits(16)))[2:]
    )
    bp.make_dataset(
        dataset_id=project_id,
        store=xnat_repository,
        name="",
    )
    dataset = access_dataset(
        project_id, access_method, xnat_repository, xnat_archive_dir, run_prefix
    )
    dataset.save()

    command = XnatCommand(**command_spec)

    # Start generating the arguments for the CLI
    # Add source to loaded dataset
    command.execute(
        address=dataset.address,
        input_values=[
            ("in_file1", "scan1"),
            ("in_file2", "scan2"),
        ],
        output_values=[
            ("out_file", "sink_file"),
        ],
        parameter_values=[
            ("duplicates", str(duplicates)),
        ],
        raise_errors=True,
        worker="debug",
        work_dir=str(work_dir),
        loglevel="debug",
        dataset_hierarchy=",".join(bp.hierarchy),
        pipeline_name="test_pipeline",
        save_frameset=True,
    )
    # Add source column to saved dataset
    reloaded = dataset.reload()
    sink = reloaded["sink_file"]
    assert len(sink) == reduce(mul, bp.dim_lengths)
    fnames = ["file1.txt", "file2.txt"]
    expected_contents = "\n".join(fnames * duplicates)
    for item in sink:
        with open(item) as f:
            contents = f.read()
        assert contents == expected_contents
