#!/usr/bin/env python3

import os
from shutil import which

from loguru import logger

from provisioner_shared.components.runtime.errors.cli_errors import MissingUtilityException
from provisioner_shared.components.runtime.infra.context import Context


class Checks:

    _dry_run: bool = None
    _verbose: bool = None

    def __init__(self, dry_run: bool, verbose: bool):
        self._dry_run = dry_run
        self._verbose = verbose

    @staticmethod
    def create(ctx: Context) -> "Checks":
        dry_run = ctx.is_dry_run()
        verbose = ctx.is_verbose()
        logger.debug(f"Creating checks validator (dry_run: {dry_run}, verbose: {verbose})...")
        return Checks(dry_run, verbose)

    def _is_tool_exist(self, name: str) -> bool:
        if self._dry_run:
            return False
        return which(name) is not None

    def _check_tool(self, name: str) -> None:
        if self._dry_run:
            return

        if which(name) is None:
            raise MissingUtilityException(f"missing CLI tool. name: {name}")

    def _is_env_var_equals(self, name: str, value: str) -> bool:
        if self._dry_run:
            return False
        return os.environ.get(name) == value

    is_tool_exist_fn = _is_tool_exist
    check_tool_fn = _check_tool
    is_env_var_equals_fn = _is_env_var_equals
