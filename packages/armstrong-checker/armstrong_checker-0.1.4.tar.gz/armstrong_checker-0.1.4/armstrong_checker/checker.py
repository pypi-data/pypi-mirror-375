


def armstrong(number_to_check):
    digits_list = []
    adder = 0

    if not number_to_check.isnumeric():
        raise ValueError("The input must be a integer.")
        
        
    digits_list =  [int(digit) for digit in number_to_check]
    

    for digit in digits_list:
        digit = digit**len(digits_list)
        adder += digit

    return adder == int(number_to_check)


