# Semantic_Analysis_Requirements
Algorithms and programs for Semantic Analysis of Requirements
The folder contains Python programs for semantic parsing of requirements written in EARS format. The description of the modules are as follows:

Programs:
1.	SA_Algorithm.py: The main program for semantic parsing. This needs to be executed. It reads the requirements written in EARS format and produces output that answers the basic questions such as ‘What is the main task?’, ‘Who has to do it?’, ‘Is this requirement applicable only under certain conditions or state?’ and so on.
2.	Req_parser.py: This module is used by SA_Algorithm.py and implements the core algorithm.
3.	req_components.py: This module implements a component class to hold the various components of a requirement, print them.
4.	StanzaDepParserForRequirements.py: This is another utility program to generate dependency parse information as per Universal Dependency V2.0 framework. This is used for debug purposes.

Data:
1.	Requirements.txt: This file contains the requirements in EARS format that were used for testing and analysing the accuracy of the algorithms. Additional requirements can be added at the end or this file can be modified to test for new set of requirements. Each statement (a sentence) should be in a new line. If ‘#’ is found at the beginning of the newline, that sentence/line is considered to be a comment and skipped by the program.
2.	Results.txt: This is the output of the program for the set of requirements in Requirements.txt. It contains the intermediate debug output as well. 
3.	DependencyRelations.txt: This contains the output of StanzaDepParserForRequirements.py. This is again useful for debugging and analysing issues.

Note on the pre-requisites:
The program is tested in IDLE environment with Python version 3.10.2. And stanza module version 1.4.2 (and associated dependencies).
