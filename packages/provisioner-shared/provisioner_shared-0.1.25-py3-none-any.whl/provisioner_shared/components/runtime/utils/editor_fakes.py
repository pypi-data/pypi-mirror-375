#!/usr/bin/env python3

from unittest.mock import MagicMock

from provisioner_shared.components.runtime.infra.context import Context
from provisioner_shared.components.runtime.utils.editor import Editor
from provisioner_shared.test_lib.faker import TestFakes


class FakeEditor(TestFakes, Editor):
    def __init__(self, dry_run: bool, verbose: bool):
        TestFakes.__init__(self)
        Editor.__init__(self, dry_run=dry_run, verbose=verbose)

    @staticmethod
    def create(ctx: Context) -> "FakeEditor":
        fake = FakeEditor(dry_run=ctx.is_dry_run(), verbose=ctx.is_verbose())
        fake.open_file_for_edit_fn = MagicMock(side_effect=fake.open_file_for_edit_fn)
        return fake

    def open_file_for_edit_fn(self, filename: str) -> bool:
        return self.trigger_side_effect("open_file_for_edit_fn", filename)
