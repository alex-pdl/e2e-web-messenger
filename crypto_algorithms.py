from utils.crypto_utils import convert_to_ascii, convert_to_hex, string_to_list, generate_prime, modinv

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
    while len(text) > len(key) or len(text) == len(key):
        key += key  # Extend the key by appending itself
    if iteration < iterations:
        # Shift the ASCII value of each character by the last number of the ASCII value of the character of the key
        for i in range(len(text)):
            shift_value = int(str(ord(key[i]))[-1])
            shifted_char = chr((ord(text[i]) + shift_value) % 128)  # Modulo to stay within ASCII range
            new_text += shifted_char
        # Update 'text' with the result of recursing
        text = sym_encryption(new_text, key, iteration + 1, iterations)
    return text

# Decrypts the cipher
def sym_decryption(cipher, key, iteration, iterations):
    new_cipher = ""
    while len(cipher) > len(key) or len(cipher) == len(key):
        key += key  # Extend the key by appending itself
    if iteration < iterations:
        # Shift but in the opposite direction
        for i in range(len(cipher)):
            shift_value = int(str(ord(key[i]))[-1])
            shifted_char = chr((ord(cipher[i]) - shift_value) % 128)  # Modulo to stay within ASCII range
            new_cipher += shifted_char
        # Update 'cipher' with the result of recursing
        cipher = sym_decryption(new_cipher, key, iteration + 1, iterations)
    return cipher

# Generates RSA keys
def key_gen(bits):
    # Generate two large prime numbers with specified amount of bits
    p = generate_prime(bits//2)
    q = generate_prime(bits//2)
    # Calculate the modulus
    n = p * q
    # Euler's totient function
    phi_func = (p - 1) * (q - 1)
    # Using a reccomended public exponent instead of generating one
    e = 65537
    # Calculate the private exponent, this is the modular inverse of e and the result of the phi function
    d = modinv(e, phi_func)
    # Returning the public key and private key (in that order)
    return (n, e), (n, d)

def rsa_encrypt(plaintext, public_key):
    n, e = public_key
    ciphertext = []
     # Convert to ASCII number/Unicode and Encrypt each character in plaintext
    for char in plaintext:
        # Raise the ASCII/unicode representation of 'char' to the power of the public exponent 'e' modulo 'n'
        ciphertext.append(pow(ord(char), e, n))
    return ciphertext

def rsa_decrypt(ciphertext,private_key):
    n, d = private_key
    # Convert the cipher text from its string format to a list e.g. "[1234,4321]" to [1234,4321]
    ciphertext = string_to_list(ciphertext)
    plaintext = ""
    # Decrypt each number in ciphertext and convert its ASCII number representation to alphabet
    # Get the modular exponentiation of num using the private exponent and modulus
    for num in ciphertext:
        plaintext += chr(pow(num, d, n))
    return plaintext