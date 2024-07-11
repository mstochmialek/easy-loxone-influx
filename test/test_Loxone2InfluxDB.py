import unittest
from dateutil import tz
from Loxone2InfluxDB import parse_log_data


def parse(input_str):
    return parse_log_data(input_str, tz.tzutc(), tz.tzutc(), debug=True)


class ParsingTestCase(unittest.TestCase):

    def test_parsing_minimal(self):
        result = parse('2020-09-10 19:46:20;Bedroom temperature;23.0')
        self.assertEqual([{
            'time': '2020-09-10T19:46:20Z',
            'measurement': 'Bedroom temperature',
            'fields': {'value': 23.0},
            'tags': {'Source': 'Loxone'},
        }], result)

    def test_parsing_with_all_fields(self):
        result = parse('2024-12-31 00:00:00;outside-temp;alias:-0.1; T1 ;Second tag;Name:Third')
        self.assertEqual([{
            'time': '2024-12-31T00:00:00Z',
            'measurement': 'alias',
            'fields': {'value': -0.1},
            'tags': {'Source': 'Loxone', 'Tag_1': 'T1', 'Tag_2': 'Second tag', 'Name': 'Third'},
        }], result)

    def test_parsing_with_named_tags(self):
        result = parse('2024-12-31 00:00:00;any-name;1; Room : Bedroom ;Tag:Second;T3: Third')
        self.assertEqual(
            {'Source': 'Loxone', 'Room': 'Bedroom', 'Tag': 'Second', 'T3': 'Third'},
            result[0]['tags'])

    def test_parsing_with_mixed_tags(self):
        result = parse('2024-12-31 00:00:00;any-name;1; Room : Bedroom ;Second')
        self.assertEqual(
            {'Source': 'Loxone', 'Room': 'Bedroom', 'Tag_2': 'Second'},
            result[0]['tags'])

    def test_parsing_values(self):
        self.assert_value("1", 1)
        self.assert_value("1.0", 1)
        self.assert_value("-1.0", -1)
        self.assert_value("+1.0", 1)
        self.assert_value("1.314", 1.314)

    def assert_value(self, input_value, expected_value):
        result = parse('2024-12-31 00:00:00;any-name;' + input_value)
        self.assertEqual(expected_value, result[0]['fields']['value'])


if __name__ == '__main__':
    unittest.main()
