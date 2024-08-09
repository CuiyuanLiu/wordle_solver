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
        self.ref_wordLst = []
        self.ref_size = 0
        self.ref_wordDF = pd.DataFrame()
        self.lowerLst = list(string.ascii_lowercase)
        self.upperLst = list(string.ascii_uppercase)
        self.range = range(1, size + 1)

        self.letter_occurDict = dict(zip(self.lowerLst, list(0 for i in range(len(self.lowerLst)))))
        self.given_letterLst = []
    
    # Wordle Setup
    # --------------------------------------------------------------------------------------------------------------
    # Setup, if from csv, srcword_df.csv needed. if not from csv, word_list file needed.
    def setup(self, src_fromCSV: bool, txt_fname: str, csv_fname: str):
        # Read
        if (src_fromCSV):
            self.ref_wordDF = pd.read_csv(csv_fname)
        else:
            self.ref_wordDF = self.reader(txt_fname)
            self.ref_wordDF.to_csv(csv_fname)
    
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
    
    # Wordle Running
    # --------------------------------------------------------------------------------------------------------------
    def run(self):
        pass

    # Filter a recommendation word by a given list.
    def run_recommendation(self, new_letter):
        self.given_letterLst.append(new_letter)
        pass
        
    def word_classifier(self):
        return
    
    def word_infoEntropy(self, data):
        a = pd.value_counts(data) / len(data)
        return sum(np.log2(a) * a * (-1))
    

"""
wordle_Game
"""
class wordle_Game():
    def __init__(self, size) -> None:
        # Processor
        self.Processor = wordle_Processor(size)
        self.Processor.setup(src_fromCSV = True, txt_fname = "word_list.txt", csv_fname = "srcword_df.csv")
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
        if (len(ipt_word) != 5): return score
        for i, l in enumerate(list(ipt_word.lower())):
            score += self.freq_df[i + 1][l]
        return score
    
    # Function guess:
    def guess(self):
        self.answers_range["freq_index"] = self.answers_range["word"].apply(lambda x: self.calc_freqWordScore(x))
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
        print(green_lst, yellow_lst, grey_lst)
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
                if ((len(yLst) > 0) and (t[1] in yLst)):

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
        print(self.answers_range)
    
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
