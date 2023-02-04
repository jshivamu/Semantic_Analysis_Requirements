#Author: Jagadish Shivamurthy, jshivamu@gmail.com
import stanza

# Download the language model. Uncomment the line below if you have not yet downloaded the model
#stanza.download('en')


# Build a Neural Pipeline
nlp = stanza.Pipeline('en', processors = "tokenize,mwt,pos,lemma,depparse",
                      download_method=None)


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
    
    doc = nlp(sent)
    
    # Print the dependencies of the first sentence in the doc object
    # Format - (Token, Index of head, Nature of dependency)
    # Index starts from 1, 0 is reserved for ROOT
    #doc.sentences[0].print_dependencies()
    
    print('\n', RI, ':', sent)
    sent_parsed = doc.sentences[0]
    for word in sent_parsed.words:
        print(word)

    RI = RI+1
