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
        # gets the sum of that ascii list
        total = sum(ascii_values)
        # divides the sum by a specified prime number and makes it a long integer
        divisor = str(total / prime_number)
        divisor = int(divisor.replace('.', '', 1))
        for i in range(len(ascii_values)):
            if ascii_values[i-1] % prime_number != 0:
                ascii_values[i] = ascii_values[i] * (ascii_values[i-1] % prime_number)
        
        for ascii_value in ascii_values:
            # for every ascii value in the list of ascii values
            # divide by the divisor and create another long integer from that ascii value
            # then get the last three digits of that ascii value

            result = ascii_value / divisor
            result_str = str(result)
            result = str(result * 10**(int(result_str[-2:].replace('.', ''))))
            last_three_ints = int(result[-3:].replace('.', ''))

            # now if those last three digits are greater than 127, divide by the prime number until they are under 12
            # 127 is used as it is the limit of ascii values
            while last_three_ints > 127:
                last_three_ints = last_three_ints // prime_number
            ascii_version.append(last_three_ints)
        
        return hash(ascii_version, iteration, iterations, prime_number)
    else:
        return ascii_values

def hash_password(text, salt, iterations, prime_number):
    raw_values = convert_to_hex(hash(convert_to_ascii(text,salt),0,iterations,prime_number))
    formatted_values = ''.join(raw_values)
    return formatted_values

def symmetric_encryption():
    pass

def RSA():
    pass