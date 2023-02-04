#Author: Jagadish Shivamurthy, jshivamu@gmail.com
from pathlib import Path

#Our own modules
from req_components import *
from req_parser import requirement

list_of_requirements = []

def read_and_parse_requirements():
    the_file = open('requirements.txt', 'r')
    req_in_EARS_lines = the_file.readlines()

    RI = 1
    for sent in req_in_EARS_lines:
        if(not(sent[0].isalnum())): #Skip those which start with #,*, etc.
            continue
        if(len(sent) < 3):
            continue
        sent.strip() #Get rid of leading and trailing spaces and new lines
        sent = sent.replace("\n", "")
        #print('\nParsing sentence: ', sent)
        list_of_requirements.append(requirement(RI, sent))
        RI = RI + 1 #TODO: Get this from the raw text.
        
def print_req_table():
    for req in list_of_requirements:
        print('\nRI:', req.RI, ' Raw Text: ', req.raw_sent)
        for chunk in req.chunks:
            print(chunk)
        print('\n----------------\n')
            

if __name__=='__main__':
    read_and_parse_requirements()
    #print_req_table()
    for req in list_of_requirements:
        req.semantic_parse()
        #print(req)
