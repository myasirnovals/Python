def complex_calculation(a, b):
    intermediate_result = a * 2
    print(f"Intermediate Result: {intermediate_result}")

    final_result = intermediate_result + b
    print(f"Final Result: {final_result}")

    return final_result

result = complex_calculation(5, 10)
print(f"Final output: {result}")