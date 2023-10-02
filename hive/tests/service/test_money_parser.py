from django.test import TestCase

from exception.format_not_supported import FormatNotSupportedException
from hive.service.money_parser import MoneyParser


class TestMoneyParser(TestCase):

    def test_convert_penny_format_without_penny(self):
        money_parser = MoneyParser()
        result = money_parser.convert('76,873', append_penny=False)
        self.assertEqual(result, 76873)

    def test_convert_penny_format_with_penny(self):
        money_parser = MoneyParser()
        result = money_parser.convert('76,873', append_penny=True)
        self.assertEqual(result, 7687300)

    def test_convert_with_four_digit_after_coma(self):
        money_parser = MoneyParser()
        with self.assertRaises(FormatNotSupportedException):
            money_parser.convert('7,6873', append_penny=True)

    def test_convert_us_german__penny_format_with_penny(self):
        money_parser = MoneyParser()
        result = money_parser.convert('23,345.57', append_penny=True)
        self.assertEqual(result, 2334557)

    def test_convert_other_format_with_penny(self):
        money_parser = MoneyParser()
        result = money_parser.convert('123 456 789.123', append_penny=True)
        self.assertEqual(result, 12345678912)

    def test_convert_other_format_without_penny(self):
        money_parser = MoneyParser()
        result = money_parser.convert('123 456 789.123', append_penny=False)
        self.assertEqual(result, 123456789)

    def test_convert_integer_with_penny(self):
        money_parser = MoneyParser()
        result = money_parser.convert('12345', append_penny=True)
        self.assertEqual(result, 1234500)

    def test_convert_penny_format(self):
        money_parser = MoneyParser()
        result = money_parser.convert('39,99')
        self.assertEqual(result, 3999)

    def test_convert_us_format(self):
        money_parser = MoneyParser()
        result = money_parser.convert('23,345.57')
        self.assertEqual(result, 2334557)

    def test_convert_german_format(self):
        money_parser = MoneyParser()
        result = money_parser.convert('23.345,57')
        self.assertEqual(result, 2334557)

    def test_convert_german_format_without_penny(self):
        money_parser = MoneyParser()
        result = money_parser.convert('76.873,00', append_penny=False)
        self.assertEqual(result, 7687300)

    def test_convert_single_decimal_digit(self):
        money_parser = MoneyParser()
        result = money_parser.convert('234.5')
        self.assertEqual(result, 23450)

    def test_convert_single_decimal_digit_with_penny(self):
        money_parser = MoneyParser()
        result = money_parser.convert('234.5', append_penny=True)
        self.assertEqual(result, 23450)

    def test_convert_ends_with_decimal_separator(self):
        money_parser = MoneyParser()
        result = money_parser.convert('123.')
        self.assertEqual(result, 12300)

    def test_convert_ends_with_decimal_separator_without_penny(self):
        money_parser = MoneyParser()
        result = money_parser.convert('123.', append_penny=False)
        self.assertEqual(result, 123)

    def test_convert_ends_with_decimal_separator_with_penny(self):
        money_parser = MoneyParser()
        result = money_parser.convert('123.', append_penny=True)
        self.assertEqual(result, 12300)

    def test_convert_invalid_format(self):
        money_parser = MoneyParser()
        with self.assertRaises(FormatNotSupportedException):
            money_parser.convert('abc')

    def test_convert_empty_string(self):
        money_parser = MoneyParser()
        with self.assertRaises(FormatNotSupportedException):
            money_parser.convert('')

    def test_convert_none(self):
        money_parser = MoneyParser()
        with self.assertRaises(FormatNotSupportedException):
            money_parser.convert(None)

