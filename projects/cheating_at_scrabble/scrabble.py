import wordscore
import json
import sys
from datetime import datetime
startTime = datetime.now()

#rack error check#

if len(sys.argv) < 2:
    raise Exception("No rack entered.")
    
if len(sys.argv) > 3:
    raise Exception("Please enter valid letter position argument, ex \'{\"P\": 0, \"n\": 2}\'.")

#set rack
rack = sys.argv[1].lower()

#Exceptions and error checking#

if len(rack) < 2 or len(rack) > 8:
    raise Exception("Please enter a valid rack with 2-7 letters.")
    
if list(rack).count('*') > 1 or list(rack).count('?') > 1:
    raise Exception("A max of one of each wildcard *,? is allowed")
    
for x in rack:
    if x not in 'acbedgfihkjmlonqpsrutwvyxz*?':
        raise Exception("Rack can only contain letters or wildcards *,?")


def read_word_lib(file="sowpods.txt"):
    """open txt file containing sowpods words to store in list
       trim list to words 7 letter or less, return list
    """
    
    with open(file,"r") as infile:
        raw_input = infile.readlines()
        data = [datum.strip('\n') for datum in raw_input]
        return [word.lower() for word in data if len(word)<=7] 

def can_form_word(word):
    """Confirm if word can be formed 
    with letters contained in the rack
    """
    
    rack_letters = list(rack)
    
    for letter in word:
        if letter in rack_letters:
            rack_letters.remove(letter)
        elif '*' in rack_letters:
            rack_letters.remove('*')
        elif '?' in rack_letters:
            rack_letters.remove('?') 
        else:
            return False
    return True

def words_pos(pos, v_words):
    """EXTRA CREDIT func: Returns valid words
    that match letter: position pairs in pos dict
    """
    
    #list of words that meet letter:position pairs
    pos_words = [word for word in v_words for k, v in pos.items() 
                 if len(word) > v if word[v] == k.lower()]
    
    #filters to words that meet all positional reqs, not just one
    pos_words2 = [word for word in pos_words 
                  if pos_words.count(word)==len(pos)] 
    
    #remove duplicates
    return list(set(pos_words2)) 

def permute(rack):
    """For a given rack of letters,print the words 
    in the sowpod list that pass form_word_check, 
    in descending order of their Scrabble scores.
    """
    
    valid_words = [word for word in read_word_lib() if can_form_word(word)]
    
    #Extra Credit conditional
    """ An entry at position 2 allows user to specify 
    that a certain letter has to be at a certain location.
    '{"Letter" : Index}' dict is entered in position 2."""
    
    if len(sys.argv)==3: # check if arg at position 2 of cmd line
        pos = dict(json.loads(sys.argv[2])) #store json object from cmd as dict
        valid_words = words_pos(pos, valid_words) #run word_pos using pos dict
                 
    score_list = [(wordscore.score_word(w,rack), w) for w in valid_words]
    
    # sort by score, use -x to sort descending, then by word
    score_list_sort = sorted(score_list, key = lambda x: (-x[0], x[1]))
    
    for x in score_list_sort:
        print("(%d, %s)" %x)
    print("Total number of words: ",len(score_list))
    
permute(rack)
print(datetime.now() - startTime)
