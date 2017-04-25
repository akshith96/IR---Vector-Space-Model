Text Based Search Engine Using Vector Space Model

The search engine includes an indexing component (which will take a large collection of text and produce a searchable, persistent data structure) and a searching 
component, according to the vector space model.The search engine indexes .text files only.

Requirements:
32-bit binary installation of Python 2.7 or 3.4+ (avoid the 64-bit versions)
NLTK library

Files inlcuded:
VSearch.py
Documentation.docx
README.md

Compiling and Running the Code:
Open the Vsearch.py using IDLE (Python 3.5 32 bit). Press F5 to run the code. The program prompts the user to input the file path of the corpus.

For unix based operating systems (Mac OSX/Linux) replace the following the lines 10 and 13 of the code in VSearch.py with "for file in os.listdir(directory + "/"):" and "files.append(directory + "/" + file)"
