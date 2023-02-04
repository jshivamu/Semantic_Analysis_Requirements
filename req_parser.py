#Author: Jagadish Shivamurthy, jshivamu@gmail.com
import stanza
from req_components import *


class requirement:
    # Build a Neural Pipeline
    nlp = stanza.Pipeline('en', processors = "tokenize,mwt,pos,lemma,depparse",
        download_method=None)
    #Note: attr is added newly
    #02-12-2022: As part of migrating to UD V2 (Stanza), prep is replaced by case and pobj by obl, dobj by obj. Moved nmod to main list. 
    ##22-12-2022: In V2, attr, npadvmod, nsubjpass, pcomp, relcl and xcomp are not present
    #MAIN_TOKEN_DEPS = ['advmod', 'advcl', 'attr', 'obj', 'mark', 'nmod', 'npadvmod', 'nsubj', 'nsubjpass', 'pcomp', 'obl', 'root', 'relcl', 'xcomp']
    MAIN_TOKEN_DEPS = ['advmod', 'advcl', 'obj', 'mark', 'nmod', 'nsubj', 'obl', 'root']
    #Note:acomp and nmod are added newly. 03-12-2022: case moved to CLUB list for V2. 05-12-2022: Added cop for V2
    ##22-12-2022: In V2, acomp, auxpass, neg, poss, preconj, prt, quantmod are not present
    #CLUB_WITH_HEAD_DEPS = ['acomp', 'amod', 'aux', 'auxpass', 'case', 'cc', 'ccomp', 'compound', 'conj', 'cop', 'det', 'expl', 'neg', 'nummod', 'poss', 'preconj', 'prt', 'quantmod']
    #Added 'fixed' on 03-02-2023
    CLUB_WITH_HEAD_DEPS = ['amod', 'aux', 'case', 'cc', 'ccomp', 'compound', 'conj', 'cop', 'det', 'expl', 'fixed', 'nummod']
    TO_BE_IGNORED_DEPS = ['punct'] #Add others if we find them.
    
    prev_token = None #Required to check the type in some cases.
    def form_chunks(self):
        """This function groups the words based on their interdepednces"""
        nlp_doc = requirement.nlp(self.raw_sent)
        new_sentence = [] #Create an empty list
        is_list_in_progress = False
        list_in_progress = []
        stanz_sent = nlp_doc.sentences[0]
        for token in stanz_sent.words:
            #if(self.RI == 5):
             #   print(token.text, token.id, new_sentence[-1])
            if(token.head != 0):
                head = stanz_sent.words[token.head -1]
            
            b_is_main_token = False
            b_is_to_be_clubbed = False
            for rel in requirement.MAIN_TOKEN_DEPS:
                if(token.deprel.startswith(rel)):
                    if(token.text.lower() == 'not'):
                        b_is_to_be_clubbed = True #If it is just negation, force it to be clubbed.
                    else:
                        b_is_main_token = True
                    break
                    
            if((b_is_main_token == False) and (b_is_to_be_clubbed == False)):
                for rel in requirement.CLUB_WITH_HEAD_DEPS:
                    if(token.deprel.startswith(rel)):
                        b_is_to_be_clubbed = True
                        break
            
            if b_is_main_token:
                list_in_progress.append(token)
                new_sentence.append(req_part(token, list_in_progress))
                list_in_progress = [] #Clear the list
                is_list_in_progress = False
            elif b_is_to_be_clubbed:
                #Check if this token's head has already passed. If yes,add it to req_part
                if(token.id > token.head):
                    list_in_progress.append(token)
                    #Check if the head is in the main list
                    b_head_found_in_list = False
                    for chunk in new_sentence:
                        if(chunk.root.id == token.head):
                            for tok in list_in_progress:
                                #new_sentence[itr].append_token(tok)
                                chunk.append_token(tok)
                            list_in_progress = []
                            is_list_in_progress = False
                            b_head_found_in_list = True
                            break
 
                    if(b_head_found_in_list == False):
                        #Check if the head is still in the pending list
                        if ((head in list_in_progress) == False):
                            print('Err:', self.RI, ':Unable to find the head in either of the lists:', token.text, head.text)
                            #print(new_sentence)
                        #Else, Nothing to do for now. 
                elif is_list_in_progress: #if there are already some tokens for the list, add to it.
                    list_in_progress.append(token)
                    prev_token = token
                    continue
                else:    #Start a new list.
                    is_list_in_progress = True
                    list_in_progress.append(token)
            elif token.deprel in requirement.TO_BE_IGNORED_DEPS:
                if(token.deprel != 'punct'):
                    print('War:Ignoring token ', token.text, token.deprel, ', position ', token.id)
            elif token.text == '\n': #if it is simply new line, ignore it.
                prev_token = token
                continue
            else: #Some unhandled dep. Indicates incompleteness of our program.
                print('Err:Unhandled Dep : ', self.RI, ':', token.text, token.deprel, token.id, head.text)
            prev_token = token
            #end of for token in st_sent.words: loop
        if(is_list_in_progress == True):
            print('\nWar:', self.RI, ':Leaving un accounted words at the end? ', list_in_progress)
        return new_sentence
    
    def add_child(self, parent_id, child):
        #locate the parent
        for chunk in self.chunks:
            for token in chunk.token_list:
                if(token.id == parent_id):
                    chunk.add_child(child)
                    return
        print("Err:RI:", self.RI, " Pos:", chunk.root.id, " Failed to find the parent of " + child.root.text)
        return
    
    def form_tree(self):
        for chunk in self.chunks:
            if chunk.root.deprel != 'root':
                self.add_child(parent_id = chunk.root.head, child = chunk)
    
    def __print_child_chunk(self, chunk, n):
        space_str = '';
        for i in range(1,n):
            space_str = space_str + '\t'
        this_chunk_str = space_str + chunk.to_str()
        print(this_chunk_str, ', ', chunk.root.deprel, ', ', chunk.root.id)
        for child in chunk.children:
            self.__print_child_chunk(child, n+1)
        return
    
    def print_tree(self):
        print('\nFor debugging')
        print(self.raw_sent)
        self.__print_child_chunk(self.root_chunk, 1)
        print('End of debugging\n')
        return
        
    def __init__(self, RI, sentence, parent_req = None):
        self.RI = RI
        self.raw_sent = sentence
        self.parent = parent_req
        self.importance = 'Unspecified'
        self.object = None
        self.subject = None
        self.state = None
        self.advmod = None
        self.verifiable = True
        self.obj_prep = [] #There can be more than one prepositions for objects, hence a list.
        self.sub_qualifiers = []
        self.obj_clause = None
        #self.stanz_sent = None
        self.chunks = self.form_chunks()
        #if(self.RI == 3):
         #   for ch in self.chunks:
          #      print(ch.to_str())
        self.form_tree()
        #self.parsed_parts = self.parse_sent_from_root()
        self.triggers_conditions = []
        
        
    def check_if_all_parsed(self):
        """ This method re-creates the sentence from the req_part list.
            Then it checks if the re-created sentence matches with the original
            sentence, except for the ignored elements such as punctuations. """
            
        return True #TODO: Complete this function.
    
    def __find_root_chunk(self):
        for chunk in self.chunks:
            if (chunk.root.deprel == 'root' or chunk.root.deprel == 'ROOT'):
                #print(chunk.root.deprel)
                return chunk
        return None
          
    def __handle_mark_prep_combo(self, marker):
        #It assumes that the mark+prep combo is the first part.
        if (marker.root.id != 0):
            print('Err:Marker in the middle.. unhandled: ', marker.root.id, marker.root.text)
            return None
        if (self.root_chunk.children[1].root.deprel != "prep"):
            print('Err:Not a mark-prep combo: ', self.root_chunk.children[1].root.deprel, self.root_chunk.children[1].to_str())
            return None
        if (marker.root.text.lower() == 'while'):
            return 'while'
        elif (marker.root.text.lower() == 'if'):
            return 'if'
        elif (marker.root.text.lower() == 'when'):
            return 'when'
        else :
            print('Err:Unknown marker! ', marker.to_str())
        return None
        
    def __find_importance(self):
        if(self.root_chunk.token_list[0].deprel == 'aux'):
            if(self.root_chunk.token_list[0].text.lower() == 'shall'):
                self.importance = 'Mandatory'
            elif(self.root_chunk.token_list[0].text.lower() == 'should'):
                self.importance = 'Desirable'
            elif(root_chunk.token_list[0].text.lower() == 'will'):
                self.importance = 'Optional'
            else:
                print('Err:RI: ', self.RI, ' uknown aux specifier: ', self.root_chunk.token_list[0].text)
        else:
            print('Err:RI: ', self.RI, ' Aux dep not found in root: ', self.root_chunk.token_list[0].text, self.root_chunk.token_list[0].deprel)
            
        
    def __extract_info_from_root(self):
        self.print_tree()
        self.__find_importance()
        root_position = self.root_chunk.root.id
        Marker = None
        for child in self.root_chunk.children:
            #Handle the left children first
            if(child.root.id < root_position):
                if(Marker != None):
                    if((Marker == "while") and (child.root.deprel == 'prep')):
                        self.state = child
                    else:
                        print('War:Unexpected Marker: ', Marker, ' followed by: ', child.to_str())
                    Marker = None        
                elif(child.root.deprel == 'advcl'):
                    #In V2, the while (indicator of state in EARS) becomes a mark child of advcl clause). Hence, check before assming it as trigger
                    b_while_state_found = False
                    if(len(child.children) > 0):
                        if ((child.children[0].root.deprel == 'mark') and (child.children[0].root.text.lower() == 'while')):
                            self.state = child
                            b_while_state_found = True
                            
                    if(b_while_state_found == False): #Check for triggers
                        Trig = Trigger(child)
                        if(Trig != None):
                            self.triggers_conditions.append(Trig)
                            if(Trig.trig_type == 'U'):
                                print('Err:Unknown trigger: ', Trig.to_str())
                        else:
                            print('Err:Failed to handle advcl: ')
                            self.__print_child_chunk(child, 1)
                elif((child.root.deprel == 'advmod') and (child.root.upos == 'SCONJ')):
                    #self.__print_child_chunk(child, 1)
                    Trig = Trigger(child)
                    if(Trig != None):
                        self.triggers_conditions.append(Trig)
                        if(Trig.trig_type == 'U'):
                                print('Err:Unknown trigger: ', Trig.to_str())
                    else:
                        print('Err:Failed to handle advmod+sconj: ')
                        self.__print_child_chunk(child, 1)
                elif((child.root.deprel.lower() == 'nsubj')): #and (len(child.children) == 0)):
                    self.subject = child
                    if(len(child.children) != 0):
                        for gr_child in child.children:
                            self.sub_qualifiers.append(gr_child)
                    
                elif((child.root.deprel.lower() == 'mark')):
                    Marker = self.__handle_mark_prep_combo(child)
                else:
                    print('\nErr:', self.RI, ':Unhandled dependency on left: ', child.root.deprel, ' ', child.to_str())
                   
            elif(child.root.id > root_position): #Handle the chunks after the root. Mainly the objects and its preps
                #print(child.to_str(), ' pos ', child.root.id) (03-12-2022: Added obl for V2)
                if(child.root.deprel == 'obj'):
                    self.object = child
                    for gr_child in child.children: #Handle the prep+pobjs attached the object directly
                        #if(gr_child.root.deprel == 'prep'):
                        if(gr_child.root.deprel == 'obl'):  #03-12-2022: Changed for V2 as in V2, the obl (pobj of V1) becomes head and 'case' (prep of V1) becomes child
                            self.obj_prep.append(gr_child)
                        if(gr_child.root.deprel.lower().startswith('nmod')):
                            self.obj_prep.append(gr_child)
                        else:
                            print('\nErr:Unhandled child type of object: ', gr_child.root.deprel, gr_child.to_str_with_children(2))
                #elif(child.root.deprel == 'prep'): #03-12-2022: Added case for V2
                elif(child.root.deprel == 'obl'): #03-12-2022: Added obl for V2
                    self.obj_prep.append(child)
                elif(child.root.deprel == 'npadvmod' or child.root.deprel == 'advmod' or 
                        child.root.deprel == 'obl:tmod'):
                    self.advmod = child
                    if(child.root.upos == 'ADV'):
                        self.verifiable = False
                elif(child.root.deprel == 'advcl'):
                    self.obj_clause = child
                else:
                    print('\nErr:', self.RI, ':Unhandled dependency on right: ', child.root.deprel, ' ', child.to_str())
                
        print(self)
             
    
    def __repr__(self):
        strg = '\nRI:' + str(self.RI) + ':' + self.raw_sent
        strg = strg + '\nImportance: ' + self.importance
        if(self.root_chunk != None):
            strg = strg + '\nMain Task:' + self.root_chunk.to_str()
        if(self.state != None):
            #strg = strg + '\nState:' + self.state.to_str_with_children(0)
            strg = strg + '\nState:' + self.state.to_str()
        if(len(self.triggers_conditions) > 0):
            for trig in self.triggers_conditions:
                strg = strg + '\n' + trig.to_str()
        if(self.subject is not None):
            strg = strg + '\nSubect:' + self.subject.to_str()
            if(len(self.sub_qualifiers) != 0):
                #strg = strg + '\nSubject qualifiers:'
                for gr_child in self.sub_qualifiers:
                    strg = strg + '\nSubject qualifiers:' + gr_child.to_str()
                    #strg = strg + gr_child.to_str_with_children(1)
        
        if(self.object != None):
            strg = strg + ' \nObject:' + self.object.to_str()
            if(self.obj_clause != None):
                strg = strg + '\nObj Clause:' + self.obj_clause.to_str_with_children(1)
                
        for prep in self.obj_prep:
            strg = strg + '\nObject preps:' + prep.to_str()
        if(self.advmod != None):
            strg = strg + '\nAdverbs to root: ' + self.advmod.to_str()
        strg = strg + '\nReq Verifiable:' + str(self.verifiable)
        return strg
        
       
    def __semantic_parse_EARS(self):
        #TODO: Develop this code.
        #print('\nRI:', self.RI, ':', self.raw_sent)
        #Locate the root
        root_chunk = self.__find_root_chunk()
        if(root_chunk is None):
            print('\nErr:Something went wrong. This requirement has no root')
            return
        self.root_chunk = root_chunk
        #print('\nRoot action:', root_chunk.to_str())
        #root_chunk.print_children()    #For debug only
        #self.__extract_basic_parameters()
        self.__extract_info_from_root()
        #self.print_tree()
        return
        
    def semantic_parse(self, template = 'EARS'):
        """ This method semantically parses all the parts of the requirement to 
            detect the following elements if any.
            State (while) in which this requirement is applicable
            Triggers (when) which necessiate the action specified
            Conditions (if) which must be met or not met for this requirement to be valid
            Subject (nsubj) of the requirement and associated qualifiers and prepositions
            Object (dobj) of the requirement and associated qualifiers and prepositions
            The main action (root verb). The parameter template specifis if the requirements
            are stated using a specific template. Value 'None' implies no template"""
            
        if(template == 'EARS'):
            self.__semantic_parse_EARS()
        else:
            raise TypeError('Unsupported template type')
        
        