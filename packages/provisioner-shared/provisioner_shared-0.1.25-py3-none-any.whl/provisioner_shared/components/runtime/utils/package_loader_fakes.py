#!/usr/bin/env python3

from typing import Callable, List
from unittest.mock import MagicMock

from provisioner_shared.components.runtime.infra.context import Context
from provisioner_shared.components.runtime.utils.package_loader import PackageLoader
from provisioner_shared.test_lib.faker import TestFakes


class FakePackageLoader(TestFakes, PackageLoader):
    def __init__(self, ctx: Context):
        TestFakes.__init__(self)
        PackageLoader.__init__(self, ctx, io_utils=None, process=None)

    @staticmethod
    def create(ctx: Context) -> "FakePackageLoader":
        fake = FakePackageLoader(ctx)
        fake.check_tool_fn = MagicMock(side_effect=fake.check_tool_fn)
        fake.is_tool_exist_fn = MagicMock(side_effect=fake.is_tool_exist_fn)
        fake.build_sdists_fn = MagicMock(side_effect=fake.build_sdists_fn)
        fake.load_modules_with_auto_version_check_fn = MagicMock(
            side_effect=fake.load_modules_with_auto_version_check_fn
        )
        return fake

    def is_tool_exist_fn(self, name: str) -> bool:
        return self.trigger_side_effect("is_tool_exist_fn", name)

    def check_tool_fn(self, name: str) -> None:
        return self.trigger_side_effect("check_tool_fn", name)

    def build_sdists_fn(self, project_paths: List[str], target_dist_folder: str):
        return self.trigger_side_effect("build_sdists_fn", project_paths, target_dist_folder)

    def load_modules_with_auto_version_check_fn(
        self, filter_keyword: str, import_path: str, exclusions: List[str], callback: Callable, debug: bool
    ) -> None:
        return self.trigger_side_effect(
            "load_modules_with_auto_version_check_fn", filter_keyword, import_path, exclusions, callback, debug
        )
