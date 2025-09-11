# This file is part of the pyMOR project (https://www.pymor.org).
# Copyright pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (https://opensource.org/licenses/BSD-2-Clause)

import numpy as np

from pymor.algorithms.basic import almost_equal
from pymor.algorithms.projection import project, project_to_subbasis


def test_project(operator_with_arrays, rng):
    op, mu, U, V = operator_with_arrays
    op_UV = project(op, V, U)
    assert op_UV.name == op_UV.__class__.__name__
    coeffs = rng.random(len(U))
    X = op_UV.apply(op_UV.source.make_array(coeffs), mu=mu)
    Y = op_UV.range.make_array(V.inner(op.apply(U.lincomb(coeffs), mu=mu)))
    assert np.all(almost_equal(X, Y))


def test_project_no_bases(operator):
    op, _ = operator
    op_proj = project(op, None, None)
    assert op_proj is op


def test_project_2(operator_with_arrays, rng):
    op, mu, U, V = operator_with_arrays
    op_U = project(op, None, U)
    assert op_U.name == op_U.__class__.__name__
    op_V = project(op, V, None)
    assert op_V.name == op_V.__class__.__name__
    op_U_V = project(op_U, V, None)
    assert op_U_V.name == op_U_V.__class__.__name__
    op_V_U = project(op_V, None, U)
    assert op_V_U.name == op_V_U.__class__.__name__
    op_UV = project(op, V, U)
    W = op_UV.source.make_array(rng.random(len(U)))
    Y0 = op_UV.apply(W, mu=mu)
    Y1 = op_U_V.apply(W, mu=mu)
    Y2 = op_V_U.apply(W, mu=mu)
    assert np.all(almost_equal(Y0, Y1))
    assert np.all(almost_equal(Y0, Y2))


def test_project_with_product(operator_with_arrays_and_products, rng):
    op, mu, U, V, sp, rp = operator_with_arrays_and_products
    op_UV = project(op, V, U, product=rp)
    assert op_UV.name == op_UV.__class__.__name__
    coeffs = rng.random(len(U))
    X = op_UV.apply(op_UV.source.make_array(coeffs), mu=mu)
    Y = op_UV.range.make_array(rp.apply2(V, op.apply(U.lincomb(coeffs), mu=mu)))
    assert np.all(almost_equal(X, Y))


def test_project_with_product_2(operator_with_arrays_and_products, rng):
    op, mu, U, V, sp, rp = operator_with_arrays_and_products
    op_U = project(op, None, U)
    assert op_U.name == op_U.__class__.__name__
    op_V = project(op, V, None, product=rp)
    assert op_V.name == op_V.__class__.__name__
    op_U_V = project(op_U, V, None, product=rp)
    assert op_U_V.name == op_U_V.__class__.__name__
    op_V_U = project(op_V, None, U)
    assert op_V_U.name == op_V_U.__class__.__name__
    op_UV = project(op, V, U, product=rp)
    W = op_UV.source.make_array(rng.random(len(U)))
    Y0 = op_UV.apply(W, mu=mu)
    Y1 = op_U_V.apply(W, mu=mu)
    Y2 = op_V_U.apply(W, mu=mu)
    assert np.all(almost_equal(Y0, Y1))
    assert np.all(almost_equal(Y0, Y2))


def test_project_to_subbasis(operator_with_arrays, rng):
    op, mu, U, V = operator_with_arrays
    op_UV = project(op, V, U)

    for dim_range in {None, 0, len(V)//2, len(V)}:
        for dim_source in {None, 0, len(U)//2, len(U)}:
            op_UV_sb = project_to_subbasis(op_UV, dim_range, dim_source)
            assert op_UV_sb.name == op_UV.name

            assert op_UV_sb.range.dim == (op_UV.range.dim if dim_range is None else dim_range)
            assert op_UV_sb.source.dim == (op_UV.source.dim if dim_source is None else dim_source)

            range_basis = V if dim_range is None else V[:dim_range]
            source_basis = U if dim_source is None else U[:dim_source]

            op_UV_sb2 = project(op, range_basis, source_basis)

            u = op_UV_sb2.source.make_array(rng.random(len(source_basis)))

            assert np.all(almost_equal(op_UV_sb.apply(u, mu=mu),
                                       op_UV_sb2.apply(u, mu=mu)))


def test_project_to_subbasis_no_range_basis(operator_with_arrays, rng):
    op, mu, U, V = operator_with_arrays
    op_U = project(op, None, U)

    for dim_source in {None, 0, len(U)//2, len(U)}:
        op_U_sb = project_to_subbasis(op_U, None, dim_source)
        assert op_U_sb.name == op_U.name

        assert op_U_sb.range == op_U.range
        assert op_U_sb.source.dim == (op_U.source.dim if dim_source is None else dim_source)

        source_basis = U if dim_source is None else U[:dim_source]

        op_U_sb2 = project(op, None, source_basis)

        u = op_U_sb2.source.make_array(rng.random(len(source_basis)))

        assert np.all(almost_equal(op_U_sb.apply(u, mu=mu),
                                   op_U_sb2.apply(u, mu=mu)))


def test_project_to_subbasis_no_source_basis(operator_with_arrays):
    op, mu, U, V = operator_with_arrays
    op_V = project(op, V, None)

    for dim_range in {None, 0, len(V)//2, len(V)}:
        op_V_sb = project_to_subbasis(op_V, dim_range, None)
        assert op_V_sb.name == op_V.name

        assert op_V_sb.range.dim == (op_V.range.dim if dim_range is None else dim_range)
        assert op_V_sb.source == op_V.source

        range_basis = V if dim_range is None else V[:dim_range]

        op_V_sb2 = project(op, range_basis, None)

        assert np.all(almost_equal(op_V_sb.apply(U, mu=mu),
                                   op_V_sb2.apply(U, mu=mu)))
