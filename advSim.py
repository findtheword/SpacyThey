import random
from collections import Counter
simulations = 100000


def dice_roll():
    return random.randint(1, 20)


def show_outcome(nam, counter):
    total = 0
    for key, val in counter.items():
        total += key*val
    print(nam, total / simulations)



def do_run():
    adv_counter = Counter()
    reg_counter = Counter()

    for sim in range(simulations):
        outcome = dice_roll()
        outcome2 = dice_roll()
        adv_counter.update([max(outcome, outcome2), ])
        reg_counter.update([outcome])

    show_outcome('adv', adv_counter)
    show_outcome('reg', reg_counter)

do_run()