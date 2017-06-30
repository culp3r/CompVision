
basket1 = ['orange', 'banana', 'coconut', 'pineapple', 'grape']

def main():
    guess_fruit(basket1)

def guess_fruit(basket):
    user_guess = input('Guess a fruit from the basket: ')
    no_match = 0
    for fruit in range(len(basket)):
        if user_guess == basket[fruit]:
            print('Correct! {} is in the fruit basket.'.format(user_guess)) 
        else:
            no_match += 1
    if no_match == len(basket):
        print('Terrible. {} is not in the fruit basket: {}'.format(user_guess, basket))

main()
