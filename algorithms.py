import binascii

def conversion(text,covert_to):
    if str(covert_to).lower() == "bin": #converts the input to ASCII/unicode and then, to binary
        ascii_values = []
        bin_values = []
        for char in text: #converts every character to its corresponding ascii value
            ascii_value = ord(char)
            ascii_values.append(ascii_value)
        
        for value in ascii_values: #converts all ascii values to binary
            bin_nums = [128,64,32,16,8,4,2,1]
            converted = ""
#if its greater than the most significant bit (MSB), which in this case is 128, then just make it equal to MSB
            if value > bin_nums[0]:
                value = bin_nums[0]
            for i in range(len(bin_nums)):
                if (value - bin_nums[i]) > -1:
                    converted += "1"
                    value = value - bin_nums[i]
                else:
                    converted += "0"
            bin_values.append(converted)
        return bin_values
    
    elif str(covert_to).lower() == "hex": #converts the input to hexadecimal
        pass

def hash(text, salt, iterations):
    pass

def symmetric_encryption():
    pass

def RSA():
    pass