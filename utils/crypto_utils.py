import random
import sympy
import hashlib


def convert_to_ascii(text, salt):
    ascii_version = []
    value = text + salt
    # turns value in ascii list
    for character in value:
        ascii_version.append(ord(character))
    return ascii_version


def convert_to_hex(ascii_values):
    hex_values = []
    for value in ascii_values:
        hex_version = hex(value)
        hex_values.append(hex_version[2:])
    return hex_values

# Converts a string e.g. "[3123,4324,1233]" to a list [3123,4324,1233]


def string_to_list(input_string):
    # Remove brackets and split the string by commas
    elements = input_string[1:-1].split(',')
    result_list = []
    for element in elements:
        result_list.append(int(element))
    return result_list

# Deterministic prime number checker


def is_prime(number):
    # Gets every number between 2 and the square of the number + 1
    for i in range(2, int(number**0.5)+1):
        # Checks if the number is divisible by any of those numbers
        if number % i == 0:
            return False
    # If not, the number is prime
    return True


def generate_prime(bits, type="default"):
    while True:
        num = random.getrandbits(bits)
        if type == "default" and sympy.isprime(num):
            return num
        if type == "custom" and is_prime(num):
            return num

# Finds the greatest common divisor between two numbers


def extended_gcd(a, b):
    if a == 0:  # The base case
        return b, 0, 1
    else:
        # Keep recursing  'b' mod  'a' and 'a' to eventually reach the base case.
        g, x, y = extended_gcd(b % a, a)
        # When base case is reached, g will be the GCD
        # and y will contain the values that satisfy the equation g=ax+by
        # Then perform a simple calculation to find x and y
        return g, y - (b // a) * x, x

# Calculate the modular inverse of 'a' and 'm'


def modinv(a, m):
    # Use the extended Euclidean algorithm to find the greatest common divisor 'g'
    # the coefficients 'x' and 'y' such that a*x + m*y = g
    g, x, y = extended_gcd(a, m)
    # If 'a' and 'm' are coprime, return the modular inverse of 'a' modulo 'm'
    return x % m


def hash_pass(password: str) -> str:
    encodedPassword = password.encode('utf-8')
    m = hashlib.sha256()
    m.update(encodedPassword)

    return m.hexdigest()
