import random
import math
import sympy

def convert_to_ascii(text,salt):
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

def string_to_tuple(input_str):
    # Remove leading and trailing whitespace, and parentheses
    cleaned_str = input_str.strip("()")
    # Split the cleaned string into individual elements
    elements = cleaned_str.split(',')
    # Convert elements to integers and create a tuple
    result_tuple = tuple(map(int, elements))
    return result_tuple

def hash(ascii_values, iteration, iterations, prime_number):
    if iteration < iterations:
        iteration += 1
        ascii_version = []
        #make the list of ascii_values specifically a length of 48
        if len(ascii_values) != 48:
            while len(ascii_values) < 48:
                ascii_values = ascii_values * 2 
            ascii_values = ascii_values[:48]
        # gets the sum of that ascii list
        total = sum(ascii_values)
        # divides the sum by a specified prime number and removes its power of 10 making it just an integer
        divisor = str(total / prime_number)
        divisor = int(divisor.replace('.', '', 1))
        # each element in the list gets multiplied by the previous element
        for i in range(len(ascii_values)):
            if ascii_values[i] * ascii_values[i-1] != 0:
                ascii_values[i] = ascii_values[i] * ascii_values[i-1]
        
        for ascii_value in ascii_values:
            # for every ascii value in the list
            # divide by the divisor and create another integer from that ascii value
            # then get the last three digits of that ascii value

            result = ascii_value / divisor
            result_str = str(result)
            result = str(result * 10**(int(result_str[-2:].replace('.', ''))))
            last_three_ints = int(result[-3:].replace('.', ''))

            # now if those last three digits are greater than 127,perform floor devision by the prime number until each value is under under 127
            # this is because 127 is used as it is the limit of ascii values
            while last_three_ints > 127:
                last_three_ints = last_three_ints // prime_number
            ascii_version.append(last_three_ints)
        
        return hash(ascii_version, iteration, iterations, prime_number)
    else:
        return ascii_values

def hash_password(text, salt, iterations, prime_number):
    raw_values = convert_to_hex(hash(convert_to_ascii(text,salt),0,iterations,prime_number))
    formatted_values = ''.join(raw_values)
    return formatted_values[:48]

def sym_encryption(text, key, iteration, iterations):
    new_text = ""
    iteration += 1
    while len(text) > len(key):
        key = key * 2
    if iteration < iterations:
        # Shift the ASCII value of each character by the last number of the ASCII value of the character of the key
        for i in range(len(text)):
            shift_value = int(str(ord(key[i]))[-1])
            shifted_char = chr((ord(text[i]) + shift_value) % 128)  # Modulo to stay within ASCII range
            new_text += shifted_char
        # Update 'text' with the result of the recursive call
        text = sym_encryption(new_text, key, iteration, iterations)
    return text

# Decrypts the cipher
def sym_decryption(cipher, key, iteration, iterations):
    new_text = ""
    iteration += 1
    while len(cipher) > len(key):
        key = key * 2
    if iteration < iterations:
        # Shift but in the opposite direction
        for i in range(len(cipher)):
            shift_value = int(str(ord(key[i]))[-1])
            shifted_char = chr((ord(cipher[i]) - shift_value) % 128)  # Modulo to stay within ASCII range
            new_text += shifted_char
        # Update 'cipher' with the result of the recursive call
        cipher = sym_decryption(new_text, key, iteration, iterations)
    return cipher

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
        if type == "default":
            if sympy.isprime(num):
                return num
        elif type == "custom":
            if is_prime(num):
                return num

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, x, y = extended_gcd(b % a, a)
        return g, y - (b // a) * x, x

def modinv(a, m):
    g, x, y = extended_gcd(a, m)
    return x % m

def key_gen(bits):
    p = generate_prime(bits//2)
    q = generate_prime(bits//2)
    n = p * q
    phi_func = (p - 1) * (q - 1)
    e = 65537
    d = modinv(e, phi_func)
    return (n, e), (n, d)

def RSA_Encrypt(plaintext, public_key):
    n, e = public_key
    ciphertext = []
    for char in plaintext:
        ciphertext.append(pow(ord(char), e, n))
    return ciphertext

def RSA_Decrypt(ciphertext,private_key):
    n, d = private_key
    ciphertext = string_to_list(ciphertext)
    plaintext = ""
    for num in ciphertext:
        plaintext += chr(pow(num, d, n))
    return plaintext