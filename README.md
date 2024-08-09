Arthur: Cuiyuan Liu
09/08/2024

## Introduction
To do this, my strategy is to count the number of letters in each position — and choose the word with the highest total frequency of letters occurring across all positions. Before I considered about using of the information entropy, but found that a direct counting of frequency would assist attaining a more stable result.

First, we need to convert the word list into the dataset. The two input files here are
- `word_list.txt`, a downloaded list of possible words of wordle, you might change it but needed to keep its format.
- `srcword_df.csv`, a dataset generated by using the processor, you could use that by running `python data_conversion.py`

```python
from wordle_process import *
myP = wordle_Processor()
myP.setup(False, "word_list.txt", "srcword_df.csv")
```

So what kind of information we needed for our filtering logics? we notes that every time we give a guessed word would find our results have three different colors:
- `grey`, represents this letter is not in this word, or existed but is a redundant letter, represented numerically by 0.
- `yellow`, represents there exists one this letter in the word, but not in this position, represented numerically by 1.
- `green`, represents this letter is in the correct position, represented numerically by 2.

## Game Class
And to solve this issue I got the following attributes for the `Game` class, the major kernel for the analyzing, which includes:
1. `self.letter_successful_guesses`, which letters we’d guessed correctly, and in what positions.
2. `self.guesses_range_lst`, the letters in the alphabet that could be still guessed with, and any wrong guesses would be elimanted from that list.
3. `self.misplaced_dict`, letters are misplaced (correct letters but wrong positions coloured in yellow).
4. `self.answers_range`, a dataframe stored the remaining possible answers (5-letter words in wordlst).
5. `self.freq_df`, the frequency of letters in each of the 5 positions, for the remaining possible 5 letter answers (to get our guesses), so the columns is the 5 location and the rows should be the 26 letters. Once getting a correct answer for a particular column, would update that column with that letter with 1 while the remains with 0.

We can do this through our constructor function, or __init__ as it’s known. This is just a fancy function that sets attributes (properties) when we create an object using our Game class.

## How to use?
Using `python run.py`. 

Wordle game address: https://wordly.org/

Step 1: Hereby for every time getting the result, noted in turn 0 to 5, turn 0 gives the initial result:
![image01](https://github.com/user-attachments/assets/e503205e-46bf-4e7e-8b7e-5bef6d30343d | width=100)
png)
This tells us the initial guess is `sanes`, then we input it into the wordle game, would find the result like below: `[Green, Grey, Grey, Green, Grey]`
![image02](https://github.com/user-attachments/assets/c2f3d3d5-6330-46ba-bc92-570947602571 | width=100)

Step 2: This gives us a number series as `20020`, we then input it like below:
![image03](https://github.com/user-attachments/assets/21ea7a6d-e5d1-4f0e-a3ef-3c243cd302e9 | width=100)

Step 3: We then get a dataframe listed the possible solutions under current circumstances, and then we get a new recommendation which is `porae`.
![image04](https://github.com/user-attachments/assets/20221e6c-512c-437d-8c1d-9432df324d17  width=100)

If word not found, enter `-1` to remove that word. 

Step 4: Repeat step 2 and step 3, then finally we get the correct result. Scripts for `run.py` attached below:
![image05](https://github.com/user-attachments/assets/abc80bcb-df2d-4f53-b4f0-425d683d3899 | width=100)


```python
from wordle_process import *

myWordle = wordle_Game()
myWordle.calc_freqdfScore(False)

for turn in range(6):
    curr_guess = myWordle.guess()
    print(f"current turn: {turn}, guess is: {curr_guess}, size: {myWordle.answers_range.shape[0]}")
    
    if (myWordle.answers_range.shape[0] < 2):
        print(f"Congratulations!, you reached the answer {curr_guess}.")
        break

    numSeries = input()
    if (numSeries == "-1"): 
        myWordle.remove_word(curr_guess)
        continue
    myWordle.run(curr_guess, numSeries)
```
