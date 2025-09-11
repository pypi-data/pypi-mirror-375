# This file is part of the pyMOR project (https://www.pymor.org).
# Copyright pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (https://opensource.org/licenses/BSD-2-Clause)

import numpy as np
import pytest

from pymor.models.iosys import LTIModel
from pymor.reductors.h2 import IRKAReductor

pytestmark = pytest.mark.builtin


def test_irka():
    A = np.array([[-1, 0], [0, -2]])
    B = np.array([[1], [2]])
    C = np.array([[2, 1]])
    fom = LTIModel.from_matrices(A, B, C)
    irka = IRKAReductor(fom)

    rom = irka.reduce(1)
    assert isinstance(rom, LTIModel)
    assert rom.order == 1

    rom = irka.reduce(np.array([1]))
    assert isinstance(rom, LTIModel)
    assert rom.order == 1

    rom = irka.reduce({'sigma': np.array([1]),
                       'b': np.array([[1]]),
                       'c': np.array([[1]])})
    assert isinstance(rom, LTIModel)
    assert rom.order == 1

    rom = irka.reduce(LTIModel.from_matrices(np.array([[-1]]),
                                             np.array([[1]]),
                                             np.array([[1]])))
    assert isinstance(rom, LTIModel)
    assert rom.order == 1
