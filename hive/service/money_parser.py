import re

from exception.format_not_supported import FormatNotSupportedException


class MoneyParser:

    def convert(self, data, append_penny=True):
        if data is None:
            raise FormatNotSupportedException(data)

        if self.__match_us_german_penny_format(data):
            result = self.__convert_to_int(data)
            return result
        if self.__match_other_format(data):
            return self.__convert_other_format(data, append_penny)

        result = self.__remove_thousands_separator(data)
        if self.__check_decimal_digits(result):
            result = re.sub(r'[.,]', '', result)

        if result.isdigit():
            if append_penny:
                result = self.__add_penny(result)
            result = self.__convert_to_int(result)
            return result

        if self.__match_single_decimal_digit(result):
            return self.__convert_single_decimal(result)

        if self.__ends_with_decimal_separator(result):
            return self.__convert_decimal_separator(result)

        raise FormatNotSupportedException(data)

    @staticmethod
    def __convert_to_int(data):
        result = re.sub(r'[., ]', '', data)
        return int(result)

    @staticmethod
    def __remove_thousands_separator(data):
        pattern = r'[^\d.,]+|[.,](?=\d+\.\d+|$)'
        value = re.sub(pattern, '', data)

        return value

    @staticmethod
    def __check_decimal_digits(value):
        pattern = r'[.,]\d{3}(?![\d.,])'
        match = re.search(pattern, value)
        if match:
            return True
        else:
            return False

    @staticmethod
    def __add_penny(data):
        return data + '00'

    @staticmethod
    def __match_other_format(data):
        pattern = r'^(\d{1,3}( \d{3})*)\.\d{3}$'
        return re.match(pattern, data)

    @staticmethod
    def __match_us_german_penny_format(data):
        us_format = r'^((?:\d+)(?:,\d{3})+)\.(\d{2})$'
        german_format = r'^(\d{1,3}( \d{3})*)\.\d{3},\d{2}$'
        penny_format = r'^(\d+)[.,](\d{2})$'
        if re.match(us_format, data):
            return True
        if re.match(german_format, data):
            return True
        if re.match(penny_format, data):
            return True

    @staticmethod
    def __match_single_decimal_digit(data):
        return re.match(r'^\d*[.,]\d$', data)

    @staticmethod
    def __ends_with_decimal_separator(data):
        return data.endswith('.') or data.endswith(',')

    def __convert_other_format(self, data, append_penny):
        if append_penny:
            result = data[:-1]
        else:
            result = data[:-3]
        result = self.__convert_to_int(result)
        return result

    def __convert_single_decimal(self, data):
        result = self.__convert_to_int(data)
        return result * 10

    def __convert_decimal_separator(self, data):
        result = self.__convert_to_int(data)
        return result * 100
