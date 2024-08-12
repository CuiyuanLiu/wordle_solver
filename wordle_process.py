import pandas as pd
import numpy as np
import string
from collections import Counter

import warnings
warnings.filterwarnings("ignore")



# Information Entropy: 
# E(I) = \sum_{x} p(x)*log_{2}(1/p(x)) = 4.01

# Factor-1: Information Entropy
# Factor-2: Word Frequency
# 12972 = 2 * 3 * 2 * 23 * 47

class wordle_Processor():
    def __init__(self, size: int) -> None:
        self.word_size = size
        self.ref_wordLst = []
        self.ref_size = 0
        self.ref_wordDF = pd.DataFrame()
        self.lowerLst = list(string.ascii_lowercase)
        self.upperLst = list(string.ascii_uppercase)
        self.range = range(1, self.word_size + 1)

        self.letter_occurDict = dict(zip(self.lowerLst, list(0 for i in range(len(self.lowerLst)))))
        self.given_letterLst = []
    
    # Wordle Setup
    # --------------------------------------------------------------------------------------------------------------
    # Setup, if from csv, srcword_df.csv needed. if not from csv, word_list file needed.
    def setup(self, src_fromCSV: bool, txt_fname: str, csv_fname: str):
        # Read
        if (src_fromCSV):
            self.ref_wordDF = pd.read_csv(csv_fname, keep_default_na=False, na_values=['NA'])
        else:
            self.ref_wordDF = self.reader(txt_fname)
            self.ref_wordDF.to_csv(csv_fname)
        
        self.ref_wordDF[list(string.ascii_lowercase)] = self.ref_wordDF[list(string.ascii_lowercase)].astype(int)
        self.ref_wordLst = list(self.ref_wordDF["word"].unique())
        self.ref_size = len(self.ref_wordLst)
        self.letter_occurDict = self.count_letterOccurrence()
        

    # Return the basic word_dataframe from reading the txt-file.
    def reader(self, txt_name: str) -> pd.DataFrame:
        f = open(txt_name)
        wordLst = f.read().split("\n")

        # Dataframe set-up
        wordDF = pd.DataFrame({"word": wordLst})
        wordDF["word"] = wordDF["word"].apply(lambda x: self.change_UpperLower(x, True))
        
        # Count letter occurence freq.
        for letter in list(string.ascii_lowercase):
            wordDF[letter] = wordDF.apply(lambda row: 
                self.letter_wordCounter(letter, row["word"]) if (letter in list(row["word"])) else 0, axis = 1
            )
        
        for position in list(self.range):
            wordDF[position] = wordDF.apply(lambda row: list(row["word"])[position - 1], axis = 1)

        return wordDF.dropna().reset_index(drop = True)

    # Count the occurrence of a letter in a word.
    def letter_wordCounter(self, ipt_letter: str, ipt_word: str):
        l = list(ipt_word)
        c = [i for i in l if i == ipt_letter]
        return len(c)

    # If turn is True, then upper to lower, vice versa.
    def change_UpperLower(self, word: str, turn: bool):
        result = word.lower() if turn else word.upper()
        return result

    # Count the occurrence among all letters of all words.
    def count_letterOccurrence(self):
        for letter in self.lowerLst:
            try:
                self.letter_occurDict[letter] = self.ref_wordDF[letter].sum()
            except Exception as err:
                print(f"Error: count letter {letter}.\nException: the exception is {err}.")
        return self.letter_occurDict

    # Filter a recommendation word by a given list.
    def run_recommendation(self, new_letter):
        self.given_letterLst.append(new_letter)
        pass
        
    def word_infoEntropy(self, data):
        a = pd.value_counts(data) / len(data)
        return sum(np.log2(a) * a * (-1))
    

"""
wordle_Game
"""
class wordle_Strategy():
    def __init__(self, size, txt_fname, csv_fname) -> None:
        # Processor
        self.Processor = wordle_Processor(size)
        self.Processor.setup(True, txt_fname, csv_fname)
        self.range = self.Processor.range

        # Attributes
        self.guesses_range_lst = list(string.ascii_lowercase)
        self.answers_range = self.Processor.ref_wordDF
        self.list_guessed = self.Processor.ref_wordLst
        self.misplaced_dict = {}
        self.freq_df = pd.DataFrame(columns = list(self.range), index = self.guesses_range_lst).fillna(0)
        self.answer_dict = dict(zip(list(str(x) for x in list(self.range)), list(None for i in range(5))))

    # Fucntion setup.
    def setup(self):
        self.freq_df = self.calc_freqdfScore(clean = False)
    
    # Function to attain the freq_df, calculate the frequency of letters in each position.
    def calc_freqdfScore(self, clean: bool):
        if (clean):
            self.freq_df = pd.DataFrame(columns = list(self.range), index = self.guesses_range_lst).fillna(0)
        for curr_word in self.Processor.ref_wordLst:
            for i, l in enumerate(list(curr_word)):
                self.freq_df[i + 1][l] += 1
        return self.freq_df
    
    # Function to calcualte the frequency score for a single word.
    def calc_freqWordScore(self, ipt_word: str):
        score = 0
        if (len(ipt_word) != self.Processor.word_size): 
            return score
        for i, l in enumerate(list(ipt_word.lower())):
            score += self.freq_df[i + 1][l]
        return score
    
    # Function to calculate the information entropy.
    def calc_infoEntropy(self, ipt_word: str):
        N = self.answers_range.shape[0]
        n = len(ipt_word)
        Prob = list(0 for i in range(n))
        Result = 0
        for c in range(n):
            Prob[c] = self.freq_df[c].iloc(ipt_word[c]) / N
            Result = Result + (Prob[c] * np.log2(Prob[c]))

        return Result
    
    # Function guess:
    def guess(self):
        # self.answers_range["freq_index"] = self.answers_range["word"].apply(lambda x: self.calc_freqWordScore(x))
        self.answers_range["freq_index"] = np.vectorize(self.calc_freqWordScore)(self.answers_range["word"])
        self.answers_range = self.answers_range.sort_values(by = 'freq_index', ascending = False).reset_index(drop = True)
        return self.answers_range.iloc[0]["word"]
    
    # Green 2. Yellow 1, Grey 0.
    # Filtering the yellow letters first.
    def check_misplaced_letters(self, ipt_correct_dict: dict, guess_word: str):
        grey_lst, green_lst, yellow_lst = [], [], []
        for i, l in enumerate(list(ipt_correct_dict.keys())):
            if (ipt_correct_dict[l] == 0): grey_lst.append((i + 1, guess_word[l]))
            if (ipt_correct_dict[l] == 2): green_lst.append((i + 1, guess_word[l]))
            if (ipt_correct_dict[l] == 1): yellow_lst.append((i + 1, guess_word[l]))
        
        # Filter words contains the yellow color.
        # Filter the t[0] location is not corresponding value first.
        # (t[0]: location, t[1]: letter)
        # print(f"green: {green_lst}, yellow: {yellow_lst}, grey: {grey_lst}.")
        self.misplaced_dict = {}

        for t in yellow_lst:
            if (t[0] not in list(self.misplaced_dict.keys())):
                self.misplaced_dict.update({t[0]: t[1]})
            else:
                self.misplaced_dict[t[0]] += 1

            try:
                self.answers_range = self.answers_range[self.answers_range[t[1]] > 0].copy()
                self.answers_range = self.answers_range[self.answers_range[str(t[0])] != t[1]].copy()
            except Exception as err:
                print(f"Error of {guess_word, t}: {Exception}")
        # print(self.answers_range)
        # Filter out words of t[0] location in green.
        for t in green_lst:
            try:
                self.answers_range = self.answers_range[self.answers_range[str(t[0])] == t[1]].copy()
                self.answer_dict[str(t[0])] = t[1]
            except Exception as err:
                print(f"Error of {guess_word, t}: {err}")

        # Filter words of t[1] location in grey.
        for t in grey_lst:
            try:
                yLst = list(self.misplaced_dict.values())
                aLst = list(self.answer_dict.values())
                if (((len(yLst) > 0) and (t[1] in yLst)) or ((len(aLst) > 0) and (t[1] in aLst))):
                    t1_times = 0
                    dict1 = dict(Counter(self.answer_dict.values()))
                    dict2 = dict(Counter(self.misplaced_dict.values()))
                    if (t[1] in dict1.keys()): t1_times += dict1[t[1]]
                    if (t[1] in dict2.keys()): t1_times += dict2[t[1]]

                    # self.answers_range = self.answers_range[self.answers_range[str(t[0])] != t[1]].copy()
                    self.answers_range = self.answers_range[self.answers_range[t[1]] == t1_times].copy()
                else:
                    self.answers_range = self.answers_range[self.answers_range[t[1]] == 0].copy()
            except Exception as err:
                print(f"Error of {guess_word, t}: {err}")
        
        self.answers_range = self.answers_range.reset_index(drop = True)
        # print(self.answers_range)
    
    def run(self, guess_word: str, numSeries: int):
        self.check_misplaced_letters(
                ipt_correct_dict = dict(zip(
                    list(range(len(guess_word))), 
                    list(int(x) for x in list(str(numSeries)))
                )),
                guess_word = guess_word
            )
        self.calc_freqdfScore(clean = True)
    
    def remove_word(self, iptword: str):
        self.answers_range = self.answers_range[self.answers_range['word'] != iptword].copy()

"""
Class: wordle_Game runner
so the input of the function contains:
- guess_word, the target word we wanna guess.
- ipt_size, decided on which dataset we use.
"""
class wordle_GameRunner():
    def __init__(self) -> None:
        self.guess_word = ""
        self.iteration = 1
        self.size = 0
        self.myWordle = None
    
    # Setup the wordle game.
    def setup_runner(self, guess_word: str, ipt_size: int):
        self.guess_word = guess_word
        self.size = ipt_size + 2
    
    # Run the game.
    def run(self, iptWordle: wordle_Strategy):
        self.myWordle = iptWordle
        curr_guess = ""
        while ((self.iteration <= self.size) and (curr_guess != self.guess_word)):
            curr_guess = self.iterate_guess()
            self.iteration = self.iteration + 1
        return curr_guess
    
    # Convert the current word into a numSeries represents the colour.
    def get_numSeries(self, curr_word):
        lettersDict_1 = dict(zip(
            list(string.ascii_lowercase), list(0 for i in range(len(string.ascii_lowercase)))
        ))
        lettersDict_2 = lettersDict_1.copy()
        nums = list(0 for c in range(len(curr_word)))
        guessLst = list(self.guess_word)
        for c in guessLst: lettersDict_2[c] += 1
        gLst = []
        
        # Green character.
        for c in range(len(curr_word)):
            if (curr_word[c] == self.guess_word[c]):
                nums[c] = 2
                lettersDict_1[curr_word[c]] += 1
                gLst.append(c)

        # Probably this is the yellow character.
        for c in range(len(curr_word)):
            if (c in gLst): continue
            if (lettersDict_2[curr_word[c]] > 0):
                if (lettersDict_1[curr_word[c]] < lettersDict_2[curr_word[c]]):
                    lettersDict_1[curr_word[c]] += 1
                    nums[c] = 1
                else:
                    nums[c] = 0
            # Probably this is the grey character.
            else:
                nums[c] = 0
        return "".join(list(str(x) for x in nums))

    # Function looping and get the guess results by iterations.
    def iterate_guess(self):
        curr_guess = self.myWordle.guess()
        try:
            
            numSeries = self.get_numSeries(curr_guess)
            print(f"Current turn: {self.iteration}, guess is: {curr_guess}, result is {numSeries}, remaining possible words list size: {self.myWordle.answers_range.shape[0]}")
            if (numSeries == "-1"): 
                self.myWordle.remove_word(curr_guess)

            if ((self.myWordle.answers_range.shape[0] == 1) or (curr_guess == self.guess_word)): 
                print(f"Congratulations!, you reached the answer {curr_guess} in {self.iteration} turns.")
                return curr_guess
            self.myWordle.run(curr_guess, numSeries)

        except Exception as err:
            print(f"Error of turn {self.iteration}: guess is {curr_guess}.\nException: {err}.")
            return curr_guess
