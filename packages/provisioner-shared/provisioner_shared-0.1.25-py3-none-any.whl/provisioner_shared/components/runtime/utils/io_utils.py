#!/usr/bin/env python3

import inspect
import os
import pathlib
import shutil
import stat
import tarfile
import tempfile
import zipfile
from shutil import copy2, copytree
from typing import Optional

from loguru import logger

from provisioner_shared.components.runtime.infra.context import Context

GIT_DIRECTORY = ".git"


class IOUtils:
    _dry_run: bool = None

    def __init__(self, ctx: Context) -> None:
        self._dry_run = ctx.is_dry_run()

    @staticmethod
    def create(ctx: Context) -> "IOUtils":
        logger.debug("Creating IO utils...")
        return IOUtils(ctx)

    def _create_temp_directory(self, maybe_prefix: Optional[str]) -> str:
        if self._dry_run:
            return "DRY_RUN_RESPONSE"
        folder_name_prefix = maybe_prefix if maybe_prefix else "provisioner-temp"
        temp_dir = tempfile.mkdtemp(prefix=folder_name_prefix)
        logger.debug("Created temp directory: {}".format(temp_dir))
        return temp_dir

    def _create_directory(self, folder_path) -> str:
        if self._dry_run:
            return "DRY_RUN_RESPONSE"

        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        return folder_path

    def _copy_file(self, from_path: str, to_path: str):
        if self._dry_run:
            return None
        copy2(from_path, to_path)

    def _copy_directory(self, from_path: str, to_path: str):
        if self._dry_run:
            return None
        copytree(from_path, to_path, dirs_exist_ok=True)

    def _delete_directory(self, directory_path: str) -> None:
        if self._dry_run:
            return None
        if os.path.isdir(directory_path):
            shutil.rmtree(directory_path)
        else:
            logger.warning("Directory does not exist, cannot delete. path: {}", directory_path)

    def _write_file(self, content: str, file_path: str) -> str:
        return self._write_file_safe(content, os.path.basename(file_path), os.path.dirname(file_path))

    def _write_file_safe(
        self, content: str, file_name: str, dir_path: Optional[str] = None, executable: Optional[bool] = False
    ) -> str:
        if self._dry_run:
            return "DRY_RUN_RESPONSE"

        path = dir_path if dir_path else tempfile.mkdtemp(prefix="provisioner-files-")
        # Create the directory path if it does not exist
        if path and not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        path = "{}/{}".format(path, file_name)
        try:
            with open(path, "w+") as opened_file:
                opened_file.write(content)
                opened_file.close()
                logger.debug("Created file. path: {}".format(path))
                if executable:
                    file_stats = os.stat(path)
                    os.chmod(path=path, mode=file_stats.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        except Exception as error:
            logger.error("Error = {}\nFailed to create file. path: {}".format(error, path))
            raise error

        return path

    def _delete_file(self, file_path: str) -> bool:
        if self._dry_run:
            return True

        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            logger.warning("File does not exists, cannot delete. path: {}", file_path)
            return False

    def _read_file_safe(self, file_path: str) -> str:
        if self._dry_run:
            return "DRY_RUN_RESPONSE"

        content = None
        try:
            with open(file_path, "r+") as opened_file:
                content = opened_file.read()
                opened_file.close()
                logger.debug("Read file successfully. path: {}".format(file_path))

        except Exception as error:
            # Debug log level on purpose since read failures might be legit in some cases
            logger.debug(error)

        return content

    def _write_symlink(self, file_path: str, symlink_path: str) -> str:
        if self._dry_run:
            return symlink_path

        # Check if symlink exists and points to the same file
        if os.path.exists(symlink_path) and os.path.islink(symlink_path):
            existing_target = os.readlink(symlink_path)
            if existing_target == file_path:
                logger.warning("Symlink already exists and points to correct file. path: {}".format(symlink_path))
                return symlink_path

        # Create parent directory if needed
        symlink_dir_path = os.path.dirname(symlink_path)
        if not os.path.exists(symlink_dir_path):
            logger.debug("Symlink folder path does not exist. creating path at: {}".format(symlink_dir_path))
            os.makedirs(symlink_dir_path, exist_ok=True)

        # Remove existing symlink if it points to a different file
        if os.path.exists(symlink_path):
            os.remove(symlink_path)

        os.symlink(src=file_path, dst=symlink_path)
        logger.debug("Created symlink. path: {}".format(symlink_path))
        return symlink_path

    def _read_symlink(self, symlink_path: str) -> str:
        if self._dry_run:
            return "DRY_RUN_RESPONSE"
        real_path = self._get_symlink_real_path(symlink_path)
        return self._read_file_safe(real_path)

    def _get_symlink_real_path(self, symlink_path: str) -> str:
        if self._dry_run:
            return "DRY_RUN_RESPONSE"
        return os.readlink(symlink_path) if os.path.islink(symlink_path) else symlink_path

    def _remove_symlink(self, symlink_path: str) -> None:
        if self._dry_run:
            return None
        if self._is_empty(symlink_path) and self._is_symlink(symlink_path):
            os.remove(symlink_path)
            logger.debug("Deleted symlink. path: {}".format(symlink_path))

    def _symlink_exists(self, symlink_path: str) -> bool:
        if self._dry_run:
            return True
        return os.path.exists(symlink_path)

    def _file_exists(self, file_path: str) -> bool:
        if self._dry_run:
            return True
        return os.path.exists(file_path)

    def _is_empty(self, file_path: str) -> bool:
        if self._dry_run:
            return False
        return os.path.isfile(file_path) and os.stat(file_path).st_size == 0

    def _is_symlink(self, file_path: str) -> bool:
        if self._dry_run:
            return True
        return os.path.islink(file_path)

    def _is_archive(self, file_path: str) -> bool:
        if self._dry_run:
            return True
        return self._file_exists(file_path) and file_path.endswith((".tar", ".zip", ".tar.gz"))

    def _unpack_archive(self, file_path: str) -> str:
        if self._dry_run:
            return "DRY_RUN_RESPONSE"
        """
        Unpack and return the parent directory path
        """
        if not self._file_exists(file_path):
            raise FileNotFoundError(file_path)

        suffix = pathlib.Path(file_path).suffix
        directory = pathlib.Path(file_path).parent
        match suffix:
            case ".zip":
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(directory)
            case ".tar":
                with tarfile.open(file_path, "r") as tar:
                    tar.extractall(path=directory)
            case ".gz":
                with tarfile.open(file_path, "r:gz") as tar:
                    tar.extractall(path=directory)
            case _:
                raise ValueError(f"Archive not supported, cannot be unpacked. name: {suffix}")
        return directory

    def _set_file_permissions(self, file_path: str, permissions_octal: int = 0o111) -> str:
        if self._dry_run:
            return "DRY_RUN_RESPONSE"
        """
        Default to execute permissions i.e. chmod +x
        Default permission covers:
          - Read, write and execute permission for owner
          - Read and execute permission for group and others
        """
        if not self._file_exists(file_path):
            raise FileNotFoundError(file_path)

        # Get the current file permission bits
        current_permission = os.stat(file_path).st_mode
        # Set the permission bits to include execute permission for owner, group and others
        os.chmod(file_path, current_permission | permissions_octal)
        return file_path

    def _find_git_repo_root_abs_path(self, clazz) -> Optional[pathlib.Path]:
        """
        Find the root directory of a git repository by traversing up from the class location.

        Args:
            clazz: The class object to start the search from

        Returns:
            Optional[Path]: The absolute path to the git repository root if found, None otherwise
        """
        try:
            # Get the directory containing the class file
            current_path = pathlib.Path(inspect.getfile(clazz)).parent
        except Exception as e:
            logger.error("Failed to get the class file path", exc_info=e)
            return None

        abs_path = current_path.absolute()

        # Traverse up the directory tree until we find .git or reach the root
        while abs_path != abs_path.root:
            git_dir = abs_path / GIT_DIRECTORY
            if git_dir.is_dir():
                return abs_path

            # Move to the parent directory
            parent = abs_path.parent
            if parent == abs_path:  # Check if we've reached the root
                break
            abs_path = parent

        return None

    create_temp_directory_fn = _create_temp_directory
    create_directory_fn = _create_directory
    copy_file_fn = _copy_file
    copy_directory_fn = _copy_directory
    delete_directory_fn = _delete_directory
    write_file_safe_fn = _write_file_safe
    write_file_fn = _write_file
    delete_file_fn = _delete_file
    read_file_safe_fn = _read_file_safe
    write_symlink_fn = _write_symlink
    read_symlink_fn = _read_symlink
    get_symlink_real_path_fn = _get_symlink_real_path
    remove_symlink_fn = _remove_symlink
    symlink_exists_fn = _symlink_exists
    file_exists_fn = _file_exists
    is_archive_fn = _is_archive
    unpack_archive_fn = _unpack_archive
    set_file_permissions_fn = _set_file_permissions
    find_git_repo_root_abs_path_fn = _find_git_repo_root_abs_path
