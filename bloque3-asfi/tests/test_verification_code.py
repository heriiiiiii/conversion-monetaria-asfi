import unittest

from app.utils.security import generate_verification_code


class VerificationCodeTest(unittest.TestCase):
    def test_code_is_hex_and_fixed_length(self):
        code = generate_verification_code()
        self.assertEqual(len(code), 8)
        self.assertTrue(all(ch in "0123456789ABCDEF" for ch in code))


if __name__ == "__main__":
    unittest.main()
