# This file is part of the pyMOR project (https://www.pymor.org).
# Copyright pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (https://opensource.org/licenses/BSD-2-Clause)

import pytest

from pymor.core.config import _PACKAGES, config
from pymor.core.exceptions import DependencyMissingError

pytestmark = pytest.mark.builtin



def test_repr():
    repr(config)


def test_entries():
    for p in _PACKAGES:
        assert hasattr(config, 'HAVE_' + p)
        assert isinstance(getattr(config, 'HAVE_' + p), bool)
        getattr(config, p + '_VERSION')


def test_dir():
    d = dir(config)
    for p in _PACKAGES:
        assert 'HAVE_' + p in d
        assert p + '_VERSION' in d


def test_require_numpy():
    config.require('numpy')
    config.require('NUMPY')


def test_require_fail_foo():
    with pytest.raises(AttributeError):
        config.require('FOO')


def test_require_fail_missing_dependency(monkeypatch):
    monkeypatch.setitem(_PACKAGES, 'THISISNOTAPACKAGENAMETHATEXISTS', lambda: False)
    with pytest.raises(DependencyMissingError):
        config.require('THISISNOTAPACKAGENAMETHATEXISTS')
