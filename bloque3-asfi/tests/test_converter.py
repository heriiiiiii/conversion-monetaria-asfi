from decimal import Decimal
import unittest

from app.converter.currency import convert_usd_to_bs


class ConverterTest(unittest.TestCase):
    def test_convert_precision(self):
        result = convert_usd_to_bs(Decimal("100.1256"), Decimal("6.9543"))
        self.assertEqual(result, Decimal("696.3035"))


if __name__ == "__main__":
    unittest.main()
