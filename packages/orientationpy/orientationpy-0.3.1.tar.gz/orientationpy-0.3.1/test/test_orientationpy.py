import sys

import numpy
import orientationpy
import pytest
import scipy

sys.path.append("./")
sys.path.append("./test")
import generateFibres
import synth_datagen

VERBOSE = 0


# --- Generate 2D test angles from -90 to 90
@pytest.mark.parametrize("angleDeg", numpy.random.rand(10) * 180 - 90)
def test_2D_synth(angleDeg):
    sigma = 2
    boxSize = 3
    # Check that gaussian and splines are accurate enough per pixel
    im = synth_datagen.generate_synthetic_data([100, 100], angleDeg, smooth=2)[25:75, 25:75]
    for mode, angular_tolerance_2D in [
        ["gaussian", 0.5],
        ["splines", 0.5],
        ["finite_difference", 5],
    ]:
        structureTensor = orientationpy.computeGradientStructureTensor(im, sigma, mode=mode)
        orientations = orientationpy.computeOrientation(structureTensor)
        assert numpy.isclose(orientations["theta"].mean(), angleDeg, atol=angular_tolerance_2D)

    # Check that gaussian and splines are accurate enough in small boxes
    for mode in ["gaussian", "splines"]:
        structureTensor = orientationpy.computeGradientStructureTensorBoxes(im, boxSize, mode=mode)

        energy = orientationpy.computeIntensity(structureTensor)
        assert energy.mean() > 0

        orientations = orientationpy.computeOrientation(structureTensor)
        assert numpy.isclose(orientations["theta"].mean(), angleDeg, atol=angular_tolerance_2D)

        vectors = orientationpy.anglesToVectors(orientations).reshape(2, -1).T
        norms = numpy.linalg.norm(vectors, axis=1)
        assert numpy.allclose(norms, 1.0, atol=0.01)

    # Check that energy and coherency are OK, let's just do it for the pixel-level
    # Let's also check for non-square crops...
    # im = synth_datagen.generate_synthetic_data([100, 100], angleDeg, smooth=2)[35:65, 25:75]
    # gradients = orientationpy.computeGradient(im, mode="finite_difference")
    # structureTensor = orientationpy.computeStructureTensor(gradients, 2)
    # orientation, energy, coherency = orientationpy.computeOrientation(structureTensor, computeEnergy=True, computeCoherency=True)

    ## Check membrane is rejected in 2D
    # orientations = orientationpy.computeOrientation(structureTensor, mode="membrane")
    # assert orientation is None

    ## Check wrong mode is also rejected
    # orientations = orientationpy.computeOrientation(structureTensor, mode="froop")
    # assert orientation is None


def test_edge_cases():
    # Edge case 1: the 2D image detector for 1-padded 2D images
    im = synth_datagen.generate_synthetic_data([100, 100], 33, smooth=2)[25:75, 25:75]
    im = im[numpy.newaxis, ...]
    structureTensor = orientationpy.computeGradientStructureTensor(im, 2, mode="gaussian")
    print(structureTensor.shape)
    assert structureTensor.shape == (3, im.shape[-2], im.shape[-1])

    orientations = orientationpy.computeOrientation(
        structureTensor,
    )
    print(orientations["theta"].mean())
    assert numpy.allclose(numpy.mean(orientations["theta"]), 33.0, atol=0.1)
    with pytest.raises(KeyError):
        print(orientations["phi"])

    # Edge case 2: bad gradient mode
    with pytest.raises(ValueError):
        orientationpy.computeGradient(im, mode="BadMode")

    # Edge case 3: bad orientation mode
    with pytest.raises(ValueError):
        orientationpy.computeOrientation(structureTensor, mode="BadMode")

    # Edge case 4: ask for membrane mode in 2d in computeOrientation
    with pytest.raises(ValueError):
        orientationpy.computeOrientation(structureTensor, mode="membrane")

    # Edge case 5: len(structureTensor.shape) != 3 or 4 in computeOrientation
    with pytest.raises(ValueError):
        orientationpy.computeOrientation(numpy.array([1, 1, 1, 1, 1, 1]), mode="membrane")

    # Edge case 6: len(structureTensor.shape) != 3 or 4
    with pytest.raises(ValueError):
        orientationpy.computeOrientation(numpy.array([1, 1, 1, 1, 1, 1]), mode="membrane")

    # Edge case 7: non 2D or 3D case in anglesToVectors
    with pytest.raises(KeyError):
        orientationpy.anglesToVectors({"empty": "dict"})

    # Edge case 8: not-a-dict
    with pytest.raises(TypeError):
        orientationpy.anglesToVectors(structureTensor)


def test_3D_fibres():
    def genThetaPhi(rot):
        # --- Generate 3D image
        im = generateFibres.generateFibres3D(50, rotationVector=rot)
        structureTensor = orientationpy.computeGradientStructureTensor(im, sigma=2, mode="gaussian")
        orientations = orientationpy.computeOrientation(structureTensor, mode="fiber")
        return orientations["theta"], orientations["phi"]

    def genThetaPhiBoxes(rot, boxSize):
        # --- Generate 3D image
        im = generateFibres.generateFibres3D(50, rotationVector=rot)
        structureTensor = orientationpy.computeGradientStructureTensorBoxes(im, boxSize, mode="splines")
        orientations = orientationpy.computeOrientation(structureTensor, mode="fiber")
        return orientations["theta"], orientations["phi"]

    # Pointing along Z
    theta, phi = genThetaPhi([0, 0, 0])
    assert numpy.allclose(theta.mean(), 0, 0.1)
    vecZYX = orientationpy.anglesToVectors({"theta": theta, "phi": phi})
    vecZYXnorm = numpy.linalg.norm(vecZYX, axis=0)

    assert vecZYXnorm.shape == (50, 50, 50)
    assert numpy.allclose(vecZYXnorm, 1.0, atol=0.01)
    assert numpy.allclose(vecZYX[0, :, :, :], 1.0, atol=0.01)
    assert numpy.allclose(vecZYX[1, :, :, :], 0.0, atol=0.01)
    assert numpy.allclose(vecZYX[2, :, :, :], 0.0, atol=0.01)

    # Pointing along Y
    theta, phi = genThetaPhi([0, 0, 90])
    assert numpy.allclose(theta.mean(), 90, 0.1)

    # In the XY plane they are ambiguous
    phi[phi > 180] -= 180
    assert numpy.allclose(phi.mean(), 90, 0.1)

    # Pointing along X
    theta, phi = genThetaPhi([0, 90, 0])
    # In the XY plane they are ambiguous
    phi[phi >= 270] -= 360
    phi[phi >= 90] -= 180
    assert numpy.allclose(theta.mean(), 90, atol=0.1)
    assert numpy.allclose(phi.mean(), 0, atol=0.1)

    theta, phi = genThetaPhi([0, 0, 45])
    assert numpy.allclose(theta.mean(), 45, atol=0.1)
    assert numpy.allclose(phi.mean(), 90, atol=0.5)

    theta, phi = genThetaPhi([0, 0, -45])
    assert numpy.allclose(theta.mean(), 45, atol=0.1)
    assert numpy.allclose(phi.mean(), 270, atol=0.5)

    theta, phi = genThetaPhi([0, 45, 0])
    assert numpy.allclose(theta.mean(), 45, atol=0.1)
    assert numpy.allclose(phi.mean(), 180, atol=0.5)

    theta, phi = genThetaPhi([0, -45, 0])
    assert numpy.allclose(theta.mean(), 45, atol=0.1)
    assert numpy.allclose(numpy.cos(numpy.deg2rad(phi.ravel())).mean(), 1, atol=0.01)

    theta, phi = genThetaPhiBoxes([0, 0, -45], 5)
    assert numpy.allclose(theta.mean(), 45, atol=0.1)
    assert numpy.allclose(phi.mean(), 270, atol=0.5)

    # for the last case, ensure vectors are normed
    vectors = orientationpy.anglesToVectors({"theta": theta, "phi": phi}).reshape(3, -1).T
    norms = numpy.linalg.norm(vectors, axis=1)
    assert numpy.allclose(norms, 1.0, atol=0.01)

    # Bonus finite_difference for Z-aligned
    # Pointing along Z
    im = synth_datagen.generate_synthetic_data([100, 100, 100], [0, 0, 0])[25:-25, 25:-25, 25:-25]
    structureTensor = orientationpy.computeGradientStructureTensor(im, sigma=1, mode="finite_difference")
    orientations = orientationpy.computeOrientation(structureTensor, mode="fiber")
    assert numpy.allclose(orientations["theta"], 0, 1)


@pytest.mark.parametrize("anisotropy_factors", [[2, 1], [1, 3.4], [2.1, 1, 1]])
@pytest.mark.parametrize("gradient_mode", ["gaussian", "splines", "finite_difference"])
@pytest.mark.parametrize("mode", ["fiber", "membrane"])
def test_anisotropy(anisotropy_factors, gradient_mode, mode):
    dimensions = len(anisotropy_factors)

    angleDeg = 30 if dimensions == 2 else [0, 45, 0]

    # Skipping membrane mode for 2D tests because it is not defined
    if dimensions == 2 and mode == "membrane":
        return

    # TODO: implement test for membrane
    if mode == "membrane":
        return

    im = synth_datagen.generate_synthetic_data(
        [
            100,
        ]
        * dimensions,
        angleDeg,
        smooth=3,
        spacing=15,
        crop=25,
    )

    anisotropic_im = scipy.ndimage.zoom(im, 1.0 / numpy.array(anisotropy_factors), order=3)

    structureTensor = orientationpy.computeGradientStructureTensor(anisotropic_im, sigma=1, mode=gradient_mode, anisotropy=anisotropy_factors)
    orientations = orientationpy.computeOrientation(structureTensor, mode=mode)

    # atol = 5 if gradient_mode == "finite_difference" else 0.5
    atol = 5 if gradient_mode == "finite_difference" else 1.5

    if dimensions == 2:
        assert numpy.isclose(angleDeg, orientations["theta"].mean(), atol=atol)
    else:
        assert numpy.isclose(180, orientations["phi"].mean(), atol=atol)
        assert numpy.isclose(angleDeg[1], orientations["theta"].mean(), atol=atol)


@pytest.fixture(params=[3, 5, 10])
def sigma(request):
    return request.param


@pytest.fixture(params=[None, 0, 1, 2])
def block_index(request):
    return request.param


@pytest.fixture
def structure_tensor(seed, sigma, block_index):
    rng = numpy.random.default_rng(seed=seed)
    if block_index is None:
        shape = tuple([sigma * 3] * 3)
        dxs = rng.normal(size=shape)
        dys = rng.normal(size=shape)
        dzs = rng.normal(size=shape)
        gradients = (dxs, dys, dzs)
        structure_tensors = orientationpy.computeStructureTensor(gradients, sigma)
        structure_tensor = structure_tensors[:, shape[0] // 2, shape[1] // 2, shape[2] // 2]
    else:
        structure_tensor = rng.normal(size=6)
        if block_index == 0:
            structure_tensor[1] = 0
            structure_tensor[2] = 0
        if block_index == 1:
            structure_tensor[1] = 0
            structure_tensor[4] = 0
        if block_index == 2:
            structure_tensor[2] = 0
            structure_tensor[4] = 0
    return orientationpy.main._unfoldMatrix(structure_tensor)


def test_eigen(structure_tensor):
    eigen_values, eigen_vectors = orientationpy.main._eigen(structure_tensor)

    # Make unit vector
    eigen_vectors = eigen_vectors / numpy.linalg.norm(eigen_vectors, axis=0)

    # Compute the projections of the eigen vectors
    vectors = structure_tensor @ eigen_vectors

    # Check that the length of the projection matches the eigen values.
    # This should be true because the eigen vectors were normalized to be unit vectors.
    lengths = numpy.linalg.norm(vectors, axis=0)
    assert numpy.allclose(numpy.abs(eigen_values), lengths, atol=1e-10)

    # Check that Av = lambda * v is satified, where A is the matrix, v is the eigen vector and lambda is the eigenvalue.
    scaled_eigen_vectors = eigen_vectors * eigen_values
    assert numpy.allclose(vectors, scaled_eigen_vectors, atol=1e-5)


def test_computeIntensity(eigen_values, structure_tensor_from_eig_vals):
    intensity = orientationpy.computeIntensity(structure_tensor_from_eig_vals)
    expected = numpy.sum(eigen_values)
    assert numpy.allclose(intensity, expected)


def test_computeStructureDirectionality(eigen_values, structure_tensor_from_eig_vals):
    directionality = orientationpy.computeStructureDirectionality(structure_tensor_from_eig_vals)
    I1 = numpy.sum(eigen_values)
    dimensionality = len(eigen_values)
    expected = numpy.sum((eigen_values - I1 / dimensionality) ** 2) / 2
    assert numpy.allclose(directionality, expected)


def test_computeStructureType(eigen_values, structure_tensor_from_eig_vals):
    dimensionality = len(eigen_values)
    if dimensionality == 2:
        with pytest.raises(RuntimeError):
            structureType = orientationpy.computeStructureType(structure_tensor_from_eig_vals)
    elif dimensionality == 3:
        structureType = orientationpy.computeStructureType(structure_tensor_from_eig_vals)
        eigen_values = sorted(eigen_values)
        n_unique_eigen_values = len(numpy.unique(eigen_values))
        if n_unique_eigen_values == 1:
            expected = 0
        elif n_unique_eigen_values == 2:
            if eigen_values[0] == eigen_values[1]:
                expected = 1
            else:
                expected = -1
        else:
            # Don't test the case where all of the eigen values are different
            return
        assert numpy.isclose(structureType, expected)


@pytest.mark.parametrize("mode", ["gaussian", "splines", "finite_difference"])
def test_computeGradient(mode, anisotropy=numpy.ones(3)):
    d = 20
    yy, xx = numpy.mgrid[-d:d, -d:d]

    yy = yy / d * numpy.pi
    xx = xx / d * numpy.pi
    r = numpy.sqrt(yy**2 + xx**2)
    img = 25000 * (numpy.cos(r) + 1)

    expected_gradient_y = 25000 * -numpy.sin(r) * yy / r * numpy.pi / d
    expected_gradient_y = numpy.nan_to_num(expected_gradient_y)
    expected_gradient_x = 25000 * -numpy.sin(r) * xx / r * numpy.pi / d
    expected_gradient_x = numpy.nan_to_num(expected_gradient_x)

    gradients = orientationpy.computeGradient(img.astype(numpy.uint16), mode=mode)

    # Mask edge effects
    mask = numpy.zeros_like(img, dtype=bool)
    mask[3:-3, 3:-3] = True

    assert numpy.allclose(gradients[0][mask], expected_gradient_y[mask], atol=100)
    assert numpy.allclose(gradients[1][mask], expected_gradient_x[mask], atol=100)
