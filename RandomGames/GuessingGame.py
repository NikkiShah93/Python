## Just a simple guessing game!!
## It gets an input from the user and compare it with the random number.
import random

def guess_num():
    ## let's define the lower and upper bounds
    lower = 1
    upper = 5
    for i in range(10):
        try:
            guess = int(input(f"guess the number (between {lower} and {upper}): "))
        except ValueError:
            print("Oops, please enter a valid number!")
            continue
        random_number = random.randint(lower, upper)
        if guess == random_number:
            print("Congrats, you guessed it right!")
            break
        else:
            print(f"Nope, you guessed wrong. The number was {random_number}. Let's try again!")
            continue
    
    if i == 9:
        print("Sorry, you lost! Better luck next time!!")
    else:
        pass
guess_num()
