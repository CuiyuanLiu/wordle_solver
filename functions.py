import time
import pandas as pd
import string
from wordle_process import *
from english_words import english_words_lower_alpha_set

# Prepare the dataset by downloading from the english_words package. (english_words_lower_alpha_set)
def prepareEnglishWordsDS():
    set_letter = dict(zip(["4", "5", "6"], list([] for i in range(3))))
    for word in english_words_lower_alpha_set:
        # Check existence of non-ascii letter.
        exist_nonAsciiLetter = False
        for c in list(word):
            if (c not in list(string.ascii_lowercase)):
                exist_nonAsciiLetter = True

        # Distribute word into different length.
        if (exist_nonAsciiLetter): 
            continue
        else:
            if len(word) == 4: set_letter["4"].append(word)
            if len(word) == 5: set_letter["5"].append(word)
            if len(word) == 6: set_letter["6"].append(word)

    for num in ["4", "5", "6"]:
        f = open(f"Dataset/wordList{num}.txt", "a")
        write_str = "\n".join(set_letter[num])
        f.write(write_str)
        f.close()

# Convert the data into a dataframe format.
def data_conversion(ipt_size, txt_file, csv_file):
    myP = wordle_Processor(size = ipt_size)
    myP.setup(False, txt_file, csv_file)

# Test the whole set.
def testWholeSet(n):
    f = open("Dataset/wordList.txt")
    wordLst = f.read().split("\n")[:5]
    checkDict = dict(zip(wordLst, list(0 for c in range(len(wordLst)))))
    timeDict = checkDict.copy()

    for currWord in wordLst:
        print(f"Guess {currWord}:")
        start = time.time()

        myWordleS = wordle_Strategy(size = n, txt_fname = "Dataset/wordList.txt", csv_fname = "Dataset/srcword_df.csv")
        myWordleS.setup()

        myGame = wordle_GameRunner()
        myGame.setup_runner(guess_word = currWord, ipt_size = 5)
        curr_guess = myGame.run(iptWordle = myWordleS)
        end = time.time()

        checkDict[currWord] = True if (curr_guess == currWord) else False
        timeDict[currWord] = end - start

    df2 = pd.DataFrame({"check": list(checkDict.values()), "time": list(timeDict.values())})
    df2.to_csv("Testing_1.csv")

# Test the single word.
def singleTest(target_word: str, txt_fname, csv_fname):
    n = len(target_word)
    myWordleS = wordle_Strategy(n, txt_fname, csv_fname)
    myWordleS.setup()

    myGame = wordle_GameRunner()
    myGame.setup_runner(guess_word = target_word, ipt_size = n)
    curr_guess = myGame.run(iptWordle = myWordleS)

# Run the guess:
def runfn(n: int, ipt_word: str):
    try:
        assert len(ipt_word) == n
        singleTest(ipt_word, f"Dataset/wordList{n}.txt", f"Dataset/srcdata{n}.csv")
    except Exception as err:
        print(f"Error of gussing {ipt_word}, n = {n}, {err}.")

# prepareEnglishWordsDS()
# data_conversion(4, "Dataset/wordList4.txt", "Dataset/srcdata4.csv")
# data_conversion(5, "Dataset/wordList5.txt", "Dataset/srcdata5.csv")
# data_conversion(6, "Dataset/wordList6.txt", "Dataset/srcdata6.csv")
# testWholeSet(5)
# singleTest("bomb", "wordList4.txt", "srcdata4.csv")
# singleTest("apple", "wordList5.txt", "srcdata5.csv")
# singleTest("soffit", "wordList6.txt", "srcdata6.csv")
# runfn(6, "soffit")