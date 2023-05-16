import re 


def apply_regex_validation(input_string):
    return re.sub(r'[^A-Za-z0-9]', '', input_string)


def agentkey_function(name, address, city, state): 
    name = apply_regex_validation(name)
    address = apply_regex_validation(address)
    city = apply_regex_validation(city)
    state = apply_regex_validation(state)

    return name[:6]+address[:6]+city[:3]+state


def addresskey_function(address, zip):
    address = apply_regex_validation(address)

    return address[:5]+str(zip)[:3]
