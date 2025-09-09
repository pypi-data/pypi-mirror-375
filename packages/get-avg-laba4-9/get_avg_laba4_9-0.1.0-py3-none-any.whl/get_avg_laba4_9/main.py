def avg(numbers):
    """Вычисляет среднее арифметическое списка чисел"""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
