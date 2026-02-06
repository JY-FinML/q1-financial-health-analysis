import unittest
from data.fetch_yfinance import company_names

class TestCompanyNames(unittest.TestCase):
    def test_company_names_mapping(self):
        expected = {
            'KO': 'CocaCola',
            'COST': 'Costco',
            'MCD': 'McDonalds',
            'PG': 'ProcterGamble',
        }
        self.assertEqual(company_names, expected)

    def test_company_names_keys(self):
        keys = list(company_names.keys())
        self.assertIn('KO', keys)
        self.assertIn('COST', keys)
        self.assertIn('MCD', keys)
        self.assertIn('PG', keys)

if __name__ == '__main__':
    unittest.main()
