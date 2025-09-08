import numpy
import pytest


@pytest.fixture(params=[0, 1, 2])
def seed(request):
    return request.param


@pytest.fixture(params=[2, 3], ids=["2D", "3D"])
def dimensionality(request):
    return request.param


@pytest.fixture(params=["eig_equal", "eig_fibre", "eig_membrane", "eig_random", "eig_one_zero", "eig_two_zero"])
def eigen_values(request, dimensionality, seed):
    rng = numpy.random.default_rng(seed=seed)
    values = rng.random(size=3) * 2.0 * numpy.pi
    values = numpy.sort(values)
    if request.param == "eig_equal":
        values[1:] = values[0]
    elif request.param == "eig_fibre":
        values[1] = values[2]
    elif request.param == "eig_membrane":
        values[1] = values[0]
    elif request.param == "eig_random":
        pass
    elif request.param == "eig_one_zero":
        values[1] = 0
    elif request.param == "eig_two_zero":
        values[1] = 0
        values[2] = 0
    values = rng.permutation(values)
    return values


@pytest.fixture
def structure_tensor_from_eig_vals(seed, eigen_values):
    dimensionality = len(eigen_values)
    rng = numpy.random.default_rng(seed=seed)
    if dimensionality == 3:
        alpha, beta, gamma = rng.random(size=3) * 2.0 * numpy.pi
        Rz = numpy.array(
            [
                [numpy.cos(alpha), -numpy.sin(alpha), 0],
                [numpy.sin(alpha), numpy.cos(alpha), 0],
                [0, 0, 1],
            ]
        )
        invRz = Rz.copy()
        invRz[0, 1] *= -1
        invRz[1, 0] *= -1
        Ry = numpy.array(
            [
                [numpy.cos(beta), 0, numpy.sin(beta)],
                [0, 1, 0],
                [-numpy.sin(beta), 0, numpy.cos(beta)],
            ]
        )
        invRy = Ry.copy()
        invRy[0, 2] *= -1
        invRy[2, 0] *= -1
        Rx = numpy.array(
            [
                [1, 0, 0],
                [0, numpy.cos(gamma), -numpy.sin(gamma)],
                [0, numpy.sin(gamma), numpy.cos(gamma)],
            ]
        )
        invRx = Rx.copy()
        invRx[1, 2] *= -1
        invRx[2, 1] *= -1
        rotation_matrix = Rz @ Ry @ Rx
        invers_rotation_matrix = invRx @ invRy @ invRz
    elif dimensionality == 2:
        alpha = rng.random() * 2.0 * numpy.pi
        rotation_matrix = numpy.array(
            [
                [numpy.cos(alpha), -numpy.sin(alpha)],
                [numpy.sin(alpha), numpy.cos(alpha)],
            ]
        )
        invers_rotation_matrix = rotation_matrix.copy()
        invers_rotation_matrix[0, 1] *= -1
        invers_rotation_matrix[1, 0] *= -1

    structure_tensor = rotation_matrix @ numpy.diag(eigen_values) @ invers_rotation_matrix
    if dimensionality == 3:
        structure_tensor = numpy.array(
            [
                structure_tensor[0, 0],
                structure_tensor[0, 1],
                structure_tensor[0, 2],
                structure_tensor[1, 1],
                structure_tensor[1, 2],
                structure_tensor[2, 2],
            ]
        )
    elif dimensionality == 2:
        structure_tensor = numpy.array(
            [
                structure_tensor[0, 0],
                structure_tensor[0, 1],
                structure_tensor[1, 1],
            ]
        )
    structure_tensor = structure_tensor[:, numpy.newaxis]
    return structure_tensor
