#Author: Jagadish Shivamurthy, jshivamu@gmail.com
import stanza

class req_part:
    def __init__(self, root, token_list):
        self.root = root
        self.token_list = token_list
        #self.parent = None
        self.children = []
    
    def append_token(self, token):
        self.token_list.append(token)
        
    def add_child(self, child):
        self.children.append(child)
        
        
    def to_str(self):
        str1 = ''
        for token in self.token_list:
            str1 = str1 + ' ' + token.text
        return str1
        
    def to_str_with_children(self, level):
        str1 = '\n'
        for i in range(1, level):
            str1 = str1 + '\t'
        str1 = str1 + self.to_str()
        for child in self.children:
            str1 = str1 + child.to_str_with_children(level+1)
        return str1
            
           
    
    def __repr__(self):
        #TODO: Make it more informative.
        str1 = 'Text:'
        for token in self.token_list:
            str1 = str1 + ' ' + token.text
        
        str1 = str1 + '\nRoot:' + self.root.text + ' Dep:' + self.root.deprel
        #str1 = str1 + ' Head:' + self.root.head.text + ' Head Dep:' + self.root.head.dep_ + '\n'
        for child in self.children:
            str1 = str1 + ' Child:' + child.root.text
        return str1
        
    def print_children(self, depth = 0):
        #print('\n')
        prefix = ""
        for i in range(depth):
            prefix = prefix + '\t'
        print(prefix + self.to_str())
        if(len(self.children) == 0):
            return
     
        for child in self.children:
            child.print_children(depth+1)
            
class Trigger:
    """Captures the components of when triggers or if conditions as per EARS"""
    SUBJ_DEPS = ['nsubj', 'nsubj:pass']
    OBJ_DEPS = ['obj', 'pobj']   #04-12-2022: Added obl to the list for V2
    TRIG_QUAL_DEPS = ['obl'] #04-12-2022: Added obl to the list for V2
    
    def __init__(self, Clause):
        """Parse and Adv Clause and extract components of a when trigger"""
        
        i = 0
        self.advmod = None
        self.subject = None
        self.object = None
        self.verifiable = True #Assume to be good to start with
        self.prep_pobj = None
        self.sub_qualifier = None
        self.obj_qualifier = None
        self.trig_type = 'U' #U for unknown
        self.trig_qualifier = None
        
        #Handle the advmod+SCONJ combination separately
        if((Clause.root.deprel == 'advmod') and (Clause.root.upos == 'SCONJ')):
            if(Clause.root.text.lower() == 'when'):
                self.trig_type = 'W'
            elif(Clause.root.text.lower() == 'if'):
                self.trig_type = 'I'
            else:
                print('Err:Unknown trigger condition for SCONJ: ', Clause.to_str())
                return
            
            if(len(Clause.children) > 1):
                print('War: More than one child for SCONJ trigger: ', Clause.to_str())
            self.subject = Clause.children[0]

        #else:
         #   print('Unknown trigger: ', Clause.root.deprel, ', ', Clause.root.upos, ', ', Clause.root.text)
        
        self.root_verb = Clause #.root #TODO: Check and confirm that it has a VERB POS
        for child in Clause.children:
            i = i + 1
            if i==1: #Should be the when
                if(child.root.text.lower() == 'when'):
                    self.trig_type = 'W'
                elif (child.root.text.lower() == 'if'):
                    self.trig_type = 'I'
                else:
                    print('Err:Unknown trigger condition: ', child.root.text)
                    return
                continue
            if(child.root.deprel in Trigger.SUBJ_DEPS):
                self.subject = child
                if(len(child.children) > 0):
                    self.sub_qualifier = child.children[0]
                    if(len(child.children) > 1):
                        print('War:Trigger subject has more than 1 qualifier: ', child.root.text)
                        
            elif(child.root.deprel in Trigger.OBJ_DEPS):
                self.object = child
                if(len(child.children) > 0):
                    self.obj_qualifier = child.children[0]
                    if(len(child.children) > 1):
                        print('War:Trigger object has more than 1 qualifier: ', child.root.text)
            elif(child.root.deprel in Trigger.TRIG_QUAL_DEPS):
                self.trig_qualifier = child
            elif(child.root.deprel == 'advmod'):
                self.advmod = child
                if(child.root.upos == 'ADV'):
                    self.verifiable = False
            elif(child.root.deprel == 'prep'):
                self.prep_pobj = child
            else:
                print('Err:Unhandled dep for When or IF condition Trigger: ', child.to_str(), child.root.deprel)
                
        return
        
    def to_str(self):
        if(self.trig_type == 'I'):
            trigType = 'Conditional'
        elif (self.trig_type == 'W'):
            trigType = 'Event driven'
        else:
            trigType = 'Unknown'
            
        str1 = 'Trigger type: ' + trigType;
        str1 = str1 + '\n\tTrig Verifiable:' + str(self.verifiable)
        str1 = str1 + '\n\tRoot Task:' + self.root_verb.to_str()
        if(self.advmod != None):
            str1 = str1 + '\n\tadvmod:' + self.advmod.to_str()
        if(self.subject != None):
            str1 = str1 + '\n\tSubect:' + self.subject.to_str()
            if(self.sub_qualifier != None):
                str1 = str1 + '\n\t\tSub qualfier:' + self.sub_qualifier.to_str()
        if(self.object != None):
            str1 = str1 + '\n\tObject:' + self.object.to_str()
            if(self.obj_qualifier != None):
                str1 = str1 + '\n\tObj qualfier:' + self.obj_qualifier.to_str()
        if(self.prep_pobj != None):
            str1 = str1 + '\n\tPrep and its object:' + self.prep_pobj.to_str()
        if(self.trig_qualifier != None):
            str1 = str1 + '\n\tTrig Qualifier:' + self.trig_qualifier.to_str()
        return str1
        
        def __repr__(self):
            return self.to_str()