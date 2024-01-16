import binascii

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
    if iteration < iterations:
        # Shift the ASCII value of each character by the last number of the ASCII value of the character of the key
        for i in range(len(text)):
            shift_value = int(str(ord(key[i]))[-1])
            shifted_char = chr((ord(text[i]) + shift_value) % 128)  # Modulo to stay within ASCII range
            new_text += shifted_char
        # Update 'text' with the result of the recursive call
        text = sym_encryption(new_text, key, iteration, iterations)
    return text

def sym_decryption(cipher, key, iteration, iterations):
    new_text = ""
    iteration += 1
    if iteration < iterations:
        # Shift but in the opposite direction
        for i in range(len(cipher)):
            shift_value = int(str(ord(key[i]))[-1])
            shifted_char = chr((ord(cipher[i]) - shift_value) % 128)  # Modulo to stay within ASCII range
            new_text += shifted_char
        # Update 'cipher' with the result of the recursive call
        cipher = sym_decryption(new_text, key, iteration, iterations)
    return cipher

def RSA():
    pass