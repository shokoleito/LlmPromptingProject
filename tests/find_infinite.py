def find_nth_digit(n):
    digit_len = 1
    count = 9
    start = 1

    while n > digit_len * count:
        n -= digit_len * count
        digit_len += 1
        count *= 10
        start *= 10

    num = start + (n - 1) // digit_len
    idx = (n - 1) % digit_len


    return int(str(num)[idx])

def print_sequence(n):
    result = ''
    i=1
    while len(result) <= n:
        result += str(i)
        i+=1
    return int(result[n-1])

print(find_nth_digit(999)==print_sequence(999))