# SPDX-FileCopyrightText: (c) 2025 Jeff C. Jensen
# SPDX-License-Identifier: MIT

from drok_xyt01 import DrokXYT01Config, DrokXYT01State, __version__


def test_pkg_imports() -> None:
    cfg = DrokXYT01Config()
    state = DrokXYT01State(None, None, None, None, None, None)
    assert isinstance(__version__, str)
    assert isinstance(cfg, DrokXYT01Config)
    assert isinstance(state, DrokXYT01State)
