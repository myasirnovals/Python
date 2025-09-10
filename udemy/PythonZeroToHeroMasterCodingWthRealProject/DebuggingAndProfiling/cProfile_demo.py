import cProfile


def sum_of_squares(n):
    result = 0
    for i in range(1, n + 1):
        result += i ** 2

    return result


def main():
    result = sum_of_squares(1000000)
    print(f"Result: {result}")

cProfile.run('main()')