import unittest
from akademik import hitung_ipk

class TestHitungIPK(unittest.TestCase):
    def test_nilai_A(self):
        self.assertAlmostEqual(hitung_ipk([{"huruf":"A","sks":3}]),4.0)
    def test_nilai_B_dan_C(self):
        data=[{"huruf":"B","sks":3},{"huruf":"C","sks":2}]
        self.assertAlmostEqual(hitung_ipk(data),(3*3+2*2)/5)
    def test_nilai_E(self):
        data=[{"huruf":"A","sks":3},{"huruf":"E","sks":2}]
        self.assertAlmostEqual(hitung_ipk(data),(4*3+0*2)/5)
    def test_nilai_F(self):
        data = [{"huruf": "A", "sks": 3}, {"huruf": "F", "sks": 2}]
        self.assertAlmostEqual(hitung_ipk(data), (4*3+0*2)/5)
    def test_nilai_tidak_dikenal(self):
        data = [{"huruf": "Z", "sks": 3}]
        with self.assertRaises(ValueError):
            hitung_ipk(data)
    def test_tidak_ada_sks(self):
        self.assertEqual(hitung_ipk([]),0.0)

if __name__=="__main__": unittest.main()
