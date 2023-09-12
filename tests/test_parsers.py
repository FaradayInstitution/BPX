import unittest

from bpx import parse_bpx_file


class TestParsers(unittest.TestCase):
    def test_negative_v_tol(self):
        with self.assertRaisesRegex(
            ValueError,
            "v_tol should not be negative",
        ):
            parse_bpx_file("filename", -0.001)
