def get_salt():
    salt = ""

    print("The password salt must be larger than "
          "12 characters and cannot include spaces.")

    while True:
        try:
            salt = input("Please enter a salt for password hashing: ")

            if len(salt) < 12:
                raise ValueError("Salt must be at least 12 characters long.")

            elif " " in salt:
                raise ValueError("You cannot include spaces in your salt")

            break
        except ValueError as e:
            print(f"\nError: {e}")

    return salt


def get_iterations():
    iterations = 0

    while True:
        try:
            iterations = input("\n\nPlease enter the number of iterations "
                               "the hashing algorithm must go through: ")

            if not iterations.isdigit():
                iterations = 0
                raise TypeError("Value must be an integer")

            iterations = int(iterations)

            if iterations < 3 or iterations > 50:
                iterations = 0
                raise ValueError("Value must be between 3 and 50")

            break
        except Exception as e:
            print("Error:", e)

    return iterations


def get_key_size():
    key_sizes = [256, 512, 1024, 2048, 4096]
    key_size = 0

    print("\n\nChoose a key size for private public key encryption" +
          "\nYour options are: " + str(key_sizes) +
          "\nNote: Key Sizes above 2048 can slow down the program tremendously, " +
          "256 - 1024 is recommended")

    while True:
        try:
            key_size = input("\nPlease enter your choice: ")

            if not key_size.isdigit() or key_size not in str(key_sizes):
                raise ValueError(
                    "Please enter a valid integer within the list of options")

            key_size = int(key_size)
            break
        except ValueError as e:
            print("Error:", e)

    return key_size


def get_secret_key():
    secret_key = ""

    print("\nThe secret key is the encryption key of the cookies."
          "\nIt must be larger than 12 characters and cannot include spaces.")

    while True:
        try:
            secret_key = input("Please enter a secret key: ")

            if len(secret_key) < 12:
                raise ValueError("It must be at least 12 characters long.")

            elif " " in secret_key:
                raise ValueError("You cannot include spaces.")

            break
        except ValueError as e:
            print("Error:", e)

    return secret_key


def has_special_chars(string: str) -> bool:
    special_characters = []
    # users can only make usernames consisting of these characters.
    allowed_characters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                          "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                          "u", "v", "w", "x", "y", "z", "0", "1", "2", "3",
                          "4", "5", "6", "7", "8", "9", "10"]
    for i in string:
        if i.lower() not in allowed_characters and i.lower() not in special_characters:
            special_characters.append(i)

    return len(special_characters) > 0


def ascii_checker(string):
    # returns a list of all characters in a string which cannot be represented as an ascii character
    # this is needed to ensure the hashing and encryption algorithms work properly
    list_of_special_chars = []
    for char in string:
        if ord(char) > 128 and char not in list_of_special_chars:
            list_of_special_chars.append(char)
    return list_of_special_chars


def string_to_tuple(input_str: str) -> tuple[int, ...]:
    # Remove leading and trailing whitespace, and parentheses
    cleaned_str = input_str.strip("()")
    # Split the cleaned string into individual elements
    elements = cleaned_str.split(',')
    # Convert elements to integers and create a tuple
    result_tuple = tuple(map(int, elements))
    return result_tuple


def is_valid_username(username: str) -> bool:
    if not isinstance(username, str):
        return False

    if has_special_chars(username):
        return False

    if len(username) < 4:
        return False

    return True
