from wordle_process import *

myWordle = wordle_Game()
myWordle.calc_freqdfScore(False)





for turn in range(6):
    curr_guess = myWordle.guess()
    print(f"current turn: {turn}, guess is: {curr_guess}, remaining possible words list size: {myWordle.answers_range.shape[0]}")
    
    if (myWordle.answers_range.shape[0] < 2):
        print(f"Congratulations!, you reached the answer {curr_guess}.")
        break

    numSeries = input()
    if (numSeries == "-1"): 
        myWordle.remove_word(curr_guess)
        continue
    myWordle.run(curr_guess, numSeries)