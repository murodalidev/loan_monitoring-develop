ones = {
    0: '', 1: 'bir', 2: 'ikki', 3: 'uch', 4: 'to`rt', 5: 'besh', 6: 'olti',
    7: 'yetti', 8: 'sakkiz', 9: 'to`qqiz', 10: 'o`n', 11: 'o`n bir', 12: 'o`n ikki',
    13: 'o`n uch', 14: 'o`n to`rt', 15: 'o`n besh', 16: 'o`n olti',
    17: 'o`n yetti', 18: 'o`n sakkiz', 19: 'o`n to`qqiz'}
tens = {
    2: 'yigirma', 3: 'o`ttiz', 4: 'qiriq', 5: 'ellik', 6: 'oltmish',
    7: 'yetmish', 8: 'sakson', 9: 'to`qson'}
illions = {
    1: 'ming', 2: 'million', 3: 'milliard', 4: 'trillion', 5: 'quadrillion',
    6: 'quintillion', 7: 'sextillion', 8: 'septillion', 9: 'octillion',
    10: 'nonillion', 11: 'decillion'}



def say_number(i):
    """
    Convert an integer in to it's word representation.

    say_number(i: integer) -> string
    """
    if i < 0:
        return _join('negative', _say_number_pos(-i))
    if i == 0:
        return 'nol'
    return _say_number_pos(i)


def _say_number_pos(i):
    if i < 20:
        return ones[i]
    if i < 100:
        return _join(tens[i // 10], ones[i % 10])
    if i < 1000:
        return _divide(i, 100, 'yuz')
    for illions_number, illions_name in illions.items():
        if i < 1000**(illions_number + 1):
            break
    return _divide(i, 1000**illions_number, illions_name)


def _divide(dividend, divisor, magnitude):
    return _join(
        _say_number_pos(dividend // divisor),
        magnitude,
        _say_number_pos(dividend % divisor),
    )


def _join(*args):
    return ' '.join(filter(bool, args))


def num2word(data):
    
    """Test cases for say_number(i)."""
    output = say_number(data)
    return output + '  so`m'
    # assert output == expected_output, \
    #     "\n    for:      {}\n    expected: {}\n    got:      {}".format(
    #         data, expected_output, output)
        


# num2word(300000000)