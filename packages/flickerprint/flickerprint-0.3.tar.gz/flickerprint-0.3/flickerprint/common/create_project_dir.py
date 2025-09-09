#!/usr/bin/env python
import argparse
import shutil
from pathlib import Path

from typing import Optional, Dict
import flickerprint as gec
from flickerprint.common import configuration


""" Create a project directory.

Outline
-------

This contains a configuration file for the experiment and the required directory
structure for outputs.

We also provide a function to check if a directory contains the file structure that we
expect.

File Structure
--------------

Each batch of microscopy files should be kept in a single directory, this contains the
magnitudes of the Fourier and figures such as the outline of the granules and the
fitting quality.

"""


class ExperimentDirectory:
    def __init__(self, new_dir: Path, dry=False):
        # Convert to a path in case a string is provided and find the full path
        self.new_dir = Path(new_dir).resolve()
        self.dry = dry

    # No longer using this check
    # def verify_super_directory(self):
    #     """Test if the new directory is created in an ``experiment`` directory. """
    #     parent_dir = self.new_dir.parent
    #     parent_name = parent_dir.name

    #     expected_parent_name = "experiments"
    #     if parent_name != expected_parent_name:
    #         raise IOError("New directory not in an expected experiment super directory")

    #     return parent_name == "experiments"

    def verify_directory_exists(self):
        """ Raise an error if the directory currently exists. """
        if self.new_dir.exists():
            raise ValueError(f"Provided directory {self.new_dir} already exists")

    def create_dirs(self):
        """ Create the given directories structure. """
        # Create the base directory for the experiment
        _create_dir(self.new_dir, self.dry)

        # List of sub directories to create
        directory_list = [
            "images",
            "fourier",
            "tracking",
            "tracking/outline",
            "tracking/detection",
            "fitting/",
            "fitting/spectra",
            "fitting/heatmaps",
            "figs/",
            "cache",
            "logs",
        ]

        for sub_dir in directory_list:
            sub_dir_path = self.new_dir.joinpath(sub_dir)
            _create_dir(sub_dir_path, dry=self.dry)

    def copy_config_file(self, update_vals: Optional[Dict] = None) -> Path:
        """Copy an example configuration file.

        Returns the path to the new configuration file.
        """

        # Get the configuration relative to the project root directory
        project_root = Path(gec.__file__).parent
        default_config_file = project_root / "common/defaults.yaml"
        if not default_config_file.exists():
            raise IOError(
                f"Default configuration file {default_config_file} not found."
            )

        new_config_location = self.new_dir / "config.yaml"

        # _cp(default_config_file, new_config_location, dry=self.dry)
        if not self.dry:
            configuration.write_config(update_vals, new_config_location)
        else:
            print(f"Writing configuration at {new_config_location}")
        return new_config_location


def _create_dir(newPath: Path, dry=False):
    """ Create a new directory, but catch the --dry signal. """
    if dry:
        print(f"Would create new dir at {newPath}")
        return

    newPath.mkdir()


def _cp(src: Path, dest: Path, dry=False):
    """Copy a file between the two locations.

    This is provided to catch the --dry flag."""
    if dry:
        print(f"Would copy {src} -> {dest}")
        return

    shutil.copy2(src, dest)


def main(
    project_dir: Path,
    dry: bool = False,
    parent: bool = False,
    update_vals: Optional[dict] = None,
):
    """ Create the experiment directory. """
    experiment_dir = ExperimentDirectory(project_dir, dry=dry)

    # Tests that the given directory choice is sane
    experiment_dir.verify_directory_exists()

    # Populate the directory structure
    experiment_dir.create_dirs()
    experiment_dir.copy_config_file(update_vals)


if __name__ == "__main__":
    parse_args()
