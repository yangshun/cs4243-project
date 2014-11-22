from unittest import TestCase
from app.texture_extractor import Reconstructor


class TestReconstructor(TestCase):
    
    def test_convertToVirtualPlane(self):
        reconstructor = Reconstructor((10, 20), 1, 1)
        self.assertTupleEqual(reconstructor.convertToVirtualPlane((0, 0)), (-10, 5))
        self.assertTupleEqual(reconstructor.convertToVirtualPlane((5, 10)), (0, 0))
        self.assertTupleEqual(reconstructor.convertToVirtualPlane((10, 20)), (10, -5))
        self.assertTupleEqual(reconstructor.convertToVirtualPlane((20, 10)), (0, -15))
        self.assertTupleEqual(reconstructor.convertToVirtualPlane((7.5, 5)), (-5, -2.5))

    def test_calculate3DCoordinate(self):
        reconstructor = Reconstructor((10, 20), 10, 5)
        self.assertTupleEqual(reconstructor.calculate3DCoordinate((5, 10), 10), (0, 0, 10))
        self.assertTupleEqual(reconstructor.calculate3DCoordinate((0, 0), 10), (-200, 100, 10))
        self.assertTupleEqual(reconstructor.calculate3DCoordinate((7.5, 5), 10), (-100, -50, 10))
