import sys

import h5py as h5
import numpy as np
import pytest

from nexusformat.nexus.tree import NXfield, nxgetconfig


@pytest.fixture
def string_dtype():
    return h5.special_dtype(vlen=str)


@pytest.fixture
def field():
    return NXfield(shape=(10, 5, 5), dtype=np.int16, maxshape=(20, 10, 10),
                   fillvalue=0)


@pytest.mark.parametrize("text", ["a", "abc", "αβγ"])
def test_string_field_creation(text, string_dtype):

    field = NXfield(text)

    assert field.nxvalue == text
    assert field.dtype == string_dtype
    assert field.is_string()
    assert len(field) == len(text)


@pytest.mark.parametrize("text", ["a", "abc", "αβγ"])
def test_byte_field_creation(text, string_dtype):

    field = NXfield(text, dtype='S')

    assert field.nxvalue == text
    assert field.nxdata.decode(nxgetconfig('encoding')) == text
    assert field.dtype != string_dtype
    assert field.is_string()
    assert len(field) == len(text)


@pytest.mark.parametrize(
    "arr",
    ["arr1D",
     "arr2D",
     "arr3D"])
def test_array_field_creation(arr, request):

    arr = request.getfixturevalue(arr)
    field = NXfield(arr)

    assert np.all(field.nxvalue == arr)
    assert np.all(field.nxdata == arr)
    assert field.shape == arr.shape
    assert field.dtype == arr.dtype
    assert field.size == arr.size
    assert field.is_numeric()
    assert len(field) == len(arr)
    assert field.reshape((field.size)) == NXfield(arr.reshape((arr.size)))


@pytest.mark.parametrize(
    "arr",
    ["arr1D",
     "arr2D",
     "arr3D"])
def test_binary_field_operations(arr, request):

    arr = request.getfixturevalue(arr)
    field = NXfield(arr)

    assert np.all((field+2).nxvalue == arr+2)
    assert np.all((field-2).nxvalue == arr-2)
    assert np.all((2*field).nxvalue == 2*arr)


@pytest.mark.parametrize(
    "arr",
    ["arr1D",
     "arr2D",
     "arr3D"])
def test_field_methods(arr, request):

    arr = request.getfixturevalue(arr)
    field = NXfield(arr)

    assert np.array_equal(field**2, arr**2)
    assert field.min() == np.min(arr)
    assert field.max() == np.max(arr)
    assert field.sum() == np.sum(arr)
    assert field.sum(dtype=np.float32) == np.sum(arr, dtype=np.float32)
    assert field.average() == np.average(arr)
    assert field.min(keepdims=True) == np.min(arr, keepdims=True)
    assert field.max(keepdims=True) == np.max(arr, keepdims=True)
    assert field.average(keepdims=True) == np.average(arr, keepdims=True)


@pytest.mark.parametrize(
    "arr,idx", [("arr1D", np.s_[2:5]),
                ("arr2D", np.s_[2:5, 2:5]),
                ("arr3D", np.s_[2:5, 2:5, 2:5])])
def test_field_slice(arr, idx, request):

    arr = request.getfixturevalue(arr)
    field = NXfield(arr)

    assert np.array_equal(field[idx].nxvalue, arr[idx])
    assert field[idx].shape == arr[idx].shape


def test_field_index(arr1D):

    field = NXfield(2*arr1D)

    assert field.index(10.) == 5
    assert field.index(11.) == 5
    assert field.index(11., max=True) == 6
    assert field.index(12., max=True) == 6

    field = NXfield(2*arr1D[::-1])

    assert field.index(10.) == 95
    assert field.index(11.) == 94
    assert field.index(11., max=True) == 95
    assert field.index(12., max=True) == 94


def test_field_resize(field):

    field[9] = 1

    assert field.shape == (10, 5, 5)
    assert field.sum() == 25

    field.resize((15, 5, 5))
    field[14] = 1

    assert field.shape == (15, 5, 5)
    assert field.sum() == 50

    field.resize((15, 5, 10))
    field[:, :, 9] = 1

    assert field.shape == (15, 5, 10)
    assert field[:, :, 9].sum() == 75


def test_field_printing(arr1D):

    assert str(NXfield(arr1D)) == str(arr1D)
    assert f"{NXfield(arr1D)[10]:g}" == f"{arr1D[10]:g}"


def test_field_operations(peak1D):

    from scipy.stats import moment

    assert peak1D.sum() == peak1D.nxvalue.sum()
    assert np.isclose(peak1D.average(), np.average(peak1D.nxvalue), rtol=1e-3)
    assert np.isclose(peak1D.mean(), np.mean(peak1D.nxvalue), rtol=1e-3)
    assert np.isclose(peak1D.var(), np.var(peak1D.nxvalue), rtol=1e-3)
    assert np.isclose(peak1D.std(), np.std(peak1D.nxvalue), rtol=1e-3)
    assert np.isclose(peak1D.moment(1), moment(peak1D.nxvalue, 1), rtol=1e-3)
    assert np.isclose(peak1D.moment(2), moment(peak1D.nxvalue, 2), rtol=1e-3)

@pytest.mark.parametrize(
    "arr",
    ["arr1D",
     "arr2D",
     "arr3D"])
def test_numpy_conversion(arr, request):

    arr = request.getfixturevalue(arr)
    field = NXfield(arr)

    assert np.array_equal(field, arr)
    assert np.array_equal(np.array(field, dtype=np.float32), 
                          arr.astype(np.float32))
