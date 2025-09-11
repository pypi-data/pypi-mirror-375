# Basic Calculator

A simple Python package for performing basic arithmetic operations.

## Installation

```bash
pip install basic-calculator
```

## Usage

```python
from basic_calculator import add, subtract, multiply, divide

result = add(5, 3)
print(result)  # 8

result = divide(10, 2)
print(result)  # 5.0
```

## Functions

- `add(a, b)`: Returns the sum of a and b
- `subtract(a, b)`: Returns the difference of a and b
- `multiply(a, b)`: Returns the product of a and b
- `divide(a, b)`: Returns the quotient of a and b (raises ValueError if b is 0)

## License

MIT License
