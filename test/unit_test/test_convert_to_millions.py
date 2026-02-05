import unittest
import pandas as pd
import numpy as np
from data.fetch_yfinance import convert_to_millions

class TestConvertToMillions(unittest.TestCase):
    def test_convert_to_millions_basic(self):
        df = pd.DataFrame({
            'A': [1_000_000, 2_000_000],
            'B': [3_000_000, 4_000_000],
            'C': ['x', 'y']
        })
        result = convert_to_millions(df.copy())
        self.assertAlmostEqual(result['A'][0], 1)
        self.assertAlmostEqual(result['A'][1], 2)
        self.assertAlmostEqual(result['B'][0], 3)
        self.assertAlmostEqual(result['B'][1], 4)
        self.assertEqual(result['C'][0], 'x')
        self.assertEqual(result['C'][1], 'y')

    def test_convert_to_millions_with_zero(self):
        df = pd.DataFrame({'A': [0, 1_000_000]})
        result = convert_to_millions(df.copy())
        self.assertEqual(result['A'][0], 0)
        self.assertEqual(result['A'][1], 1)

    def test_convert_to_millions_negative(self):
        df = pd.DataFrame({'A': [-1_000_000, 2_000_000]})
        result = convert_to_millions(df.copy())
        self.assertEqual(result['A'][0], -1)
        self.assertEqual(result['A'][1], 2)

    def test_convert_to_millions_floats(self):
        df = pd.DataFrame({'A': [1.5e6, 2.5e6]})
        result = convert_to_millions(df.copy())
        self.assertAlmostEqual(result['A'][0], 1.5)
        self.assertAlmostEqual(result['A'][1], 2.5)

    def test_convert_to_millions_with_nan(self):
        df = pd.DataFrame({'A': [1_000_000, np.nan, 3_000_000]})
        result = convert_to_millions(df.copy())
        self.assertEqual(result['A'][0], 1)
        self.assertTrue(np.isnan(result['A'][1]))
        self.assertEqual(result['A'][2], 3)

    def test_convert_to_millions_empty_df(self):
        df = pd.DataFrame()
        result = convert_to_millions(df.copy())
        self.assertTrue(result.empty)

    def test_convert_to_millions_no_numeric_columns(self):
        df = pd.DataFrame({'A': ['x', 'y'], 'B': ['a', 'b']})
        result = convert_to_millions(df.copy())
        self.assertEqual(result['A'][0], 'x')
        self.assertEqual(result['B'][0], 'a')

    def test_convert_to_millions_mixed_types(self):
        df = pd.DataFrame({
            'int_col': [1_000_000, 2_000_000],
            'float_col': [1.5e6, 2.5e6],
            'str_col': ['a', 'b']
        })
        result = convert_to_millions(df.copy())
        self.assertEqual(result['int_col'][0], 1)
        self.assertAlmostEqual(result['float_col'][0], 1.5)
        self.assertEqual(result['str_col'][0], 'a')

if __name__ == '__main__':
    unittest.main()
