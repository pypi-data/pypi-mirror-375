from random import randint

def IsHaram(anything: str) -> str:
    i = randint(0,1)
    if i == 0:
        h = f"{anything} is NOT a haram."
    elif i == 1:
        h = f"{anything} is a haram."
    else:
        h = "Error. Try again."
    return print(h)