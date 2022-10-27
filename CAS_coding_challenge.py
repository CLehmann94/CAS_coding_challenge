#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: gkarademir & clehmann
"""
import arxiv
import numpy as np
import os
import pandas as pd
import PyPDF2
import re
import requests
import sys
import unicodedata

from bs4 import BeautifulSoup
from contextlib import contextmanager
from urllib.request import unquote


@contextmanager
def suppress_stderr():
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr


# download pdf and check for institute/author affiliation
def read_pdf(ArxivID, institute, authors, student):
    pdf_URL = 'https://arxiv.org/pdf/'+ArxivID+'.pdf'
    pdf_page = requests.get(pdf_URL)  # open webpage

    filename = unquote(pdf_page.url).split('/')[-1]

#    download pdf
    with open(filename, 'wb') as f:
        f.write(pdf_page.content)

    pdfFileObj = open(filename, 'rb')  # open file
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    authors_aff_numbers = []

    inst_found = False
    n_inst = False
    for i in range(pdfReader.getNumPages()):  # loop through all pages,find aff
        pageObj = pdfReader.getPage(i)  # read page
        textorig = pageObj.extractText()
# remove blanks because sometimes pdfs are weird
        textorig = re.sub(' ', '', textorig)
        textorig = re.sub('-', '', textorig)  # remove hyphens
        textorig = remove_accents(textorig)  # remove accents

        text = re.sub('\n', '', textorig)  # remove linebreaks

        if not n_inst:
            if institute in text:  # check if aff is found on page
                n_inst = get_number_inst(textorig)  # get number of inst
                inst_found = True

# get author numbers
        authors_aff_numbers = get_author_numbers(text, textorig, authors,
                                                 authors_aff_numbers)

    os.remove(filename)  # delete pdf

    if inst_found:
        authors, student = match_inst_auth_numbers(n_inst, authors, student,
                                                   authors_aff_numbers)
    else:
        authors, student = False, False

    return inst_found, authors, student


# check if numbers of authors and inst agree
# agree to all authors if no numbers can be found
def match_inst_auth_numbers(n_inst, authors, student, authors_aff_numbers):

    if not n_inst:  # inst but not its number is found -> accept all
        return authors, student

# inst and its number but no author numbers found/or sth went wrong
# -> accept all
    elif np.any(np.array([i == [] for i in authors_aff_numbers])):
        return authors, student
    elif authors_aff_numbers == []:
        return authors, student

    else:  # remove authors where numbers dont match
        idx = []
# check all author numbers
        for i, ival in enumerate(authors_aff_numbers):
            aff_check = False

# check for multiple affiliation
            for k in ival:
                if np.any(n_inst == k):
                    aff_check = True  # if one number of author vs inst matches

# if affiliation is not found add index to list of items to remove
            if not aff_check:
                idx.append(i)

        if len(idx) > 0:  # remove items where the numbers disagree
            authors = np.delete(authors, np.array(idx))
            student = np.delete(student, np.array(idx))

        return authors, student


# get number of author for affiliation check
# assumes that number follows the name
def get_author_numbers(text, textorig, authors, authors_aff_numbers):
    for aut in authors:  # get numbers for authors
        aut = re.sub(' ', '', aut)  # remove spaces
        if aut in text:  # check for authors in text
            txtsplit = textorig.split(aut)  # split at author name
# only continue if name is in text once - otherwise you are at the references
            if len(txtsplit) == 2:
                before, after = txtsplit
# if aff number is behind linebreak
                new_split = after.split('\n')
# check if first element is empty
                if len(new_split[0]) == 0:
                    idx = 1
                else:
                    idx = 0

                after = after.split('\n')[idx]
# find affiliation numbers behind the name of the author, split at next letter
                first_elemnt = re.split(alphabet, after[:50])[0]
# take all numbers before it
                n = re.findall(r'\d+', first_elemnt)
                authors_aff_numbers.append(n)
    return authors_aff_numbers


# get number of institute from pdf
# assumes number is always in front of institute
def get_number_inst(textorig):
    splittext = textorig.split('\n')  # split by linebreaks

    idx = False
    for i, ival in enumerate(splittext):  # find idx of line with affiliation
        if institute in ival:
            if not idx:
                idx = np.array([i])  # create list of lines with affiliation
            else:
                idx = np.append(idx, i)

# split at inst name and take first number before the name of the
# institute to avoid taking numbers in the adress
    if np.any(idx):  # if a line is found
        for i, ival in enumerate(idx):  # go through all lines
            number = re.findall(r'\d+', splittext[ival].split(institute)[0])
            if number == []:  # if no number is found set n to False
                n = False

# otherwise add number to array (needs to be an array since multiple
# entries can be in the aff list for the institute)
            else:
                if i == 0:
                    n = np.array(number[0])
                else:
                    n = np.append(n, number[0])

    else:
        n = False  # return false if nothing is found

    return n


# Map all accented or weird letters (e.g. üäö in German) onto their
# counterpart in the alphabet (uao)
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


# Use above function on a string array and return the same array
def remove_accents_array(str_array):
    no_accent_array = np.array([])
    for string in str_array:
        no_accent_array = np.append(no_accent_array, remove_accents(string))
    no_accent_array = np.char.replace(no_accent_array, 'ø', 'o')
    return no_accent_array


def remove_hyphens(str_array):
    return np.char.replace(str_array, '-', ' ')


# read in the CAS name .csv file
def csv_file_to_names(file_path):
    first_name, last_name, student = np.array([]), np.array([]), \
      np.array([], dtype=bool)
    numpy_frame = pd.read_csv(file_path).to_numpy()
    first_name = np.append(first_name, numpy_frame[:, 0])
    first_name = np.append(first_name, numpy_frame[:, 2])
    last_name = np.append(last_name, numpy_frame[:, 1])
    last_name = np.append(last_name, numpy_frame[:, 3])
    student = np.append(student, numpy_frame[:, 4])
    student = np.append(student, numpy_frame[:, 4])
    return first_name, last_name, student


# def check institue and authors
def check_institute(ArxivID, institute, SwinAuth, student):
    with suppress_stderr():  # check for aff
        swin, SwinAuth, student = read_pdf(ArxivID, institute, SwinAuth,
                                           student)

# search arxiv for paper
    if swin:
        search = arxiv.Search(id_list=[ArxivID])

# print information -> to be saved in some sort of output
        for result in search.results():
            print('Title:')
            print(result.title)
            print('')
            print('ArXiv-Link: https://arxiv.org/abs/'+ArxivID)
            print('')
            print('Authors:')
            print(*result.authors, sep=', ')
            print('')
            print('CAS Affiliates:')

            for i, iauth in enumerate(SwinAuth):
                if student[i]:
                    addon = ' (Student)'
                else:
                    addon = ''
                print(iauth+addon)

            print('')
            print('Status:')
# check for paper status
# ignore first letter because of capitalization
            if result.comment is not None:
                if 'ccepted' in result.comment:
                    print('Accepted')
                elif 'ubmitted' in result.comment:
                    print('Submitted')
                elif 'ublished' in result.comment:
                    print('Published')
                else:
                    print('unknown')
            else:
                print('unknown ')

            print('')
            print('Journal:')
# check in journal ref if avaliable
            if result.journal_ref is not None:
                journal = check_journal(result.journal_ref)  # check journal
                print(journal)
            elif result.comment is not None:  # otherwise check in comment
                journal = check_journal(result.comment)
                print(journal)
            else:
                print('unknown')

            print("----------")

        return True
    else:
        return False


# check if journal is mentioned in comment by checking with provided list
def check_journal(text):
    journal_check = [i in text for i in journal_list]

    idx = np.where(np.array(journal_check))[0]

    if len(idx) == 0:
        return 'unknown'
# only return abbrevitations - expand list for more
# journals/abbreviations if needed
    else:  # if two are true - take the first one...
        if journal_list[idx[0]] == 'Monthly Notices of the Royal\
          Astronomical Society':
            return 'MNRAS'
        if journal_list[idx[0]] == 'Annual Review of Astronomy and \
          Astrophysics':
            return 'ARAA'
        if journal_list[idx[0]] == 'Astronomy & Astrophysics':
            return 'A&A'
        if journal_list[idx[0]] == 'Astrophysical Journal':
            return 'ApJ'
        if journal_list[idx[0]] == 'Astrophysical Journal Letters':
            return 'ApJL'
        if journal_list[idx[0]] == 'Astrophysical Journal Supplement Series':
            return 'ApJS'
        if journal_list[idx[0]] == 'Publications of the Astronomical Society \
          of Australia':
            return 'PASA'

        else:
            return journal_list[idx[0]]


# This function matches the first name of Authors. Just the first letter
# and the first name are accepted in this regard. The list name
# cannot be shortened.
def name_match(A_list, Arxiv, last_name=False):
    for name in A_list:  # names of CAS authors
        for i in range(len(Arxiv)):  # names of Arxiv authors
            if last_name is True:  # Only full last names
                if Arxiv[i] == name:
                    return True
            else:  # First names can be abbreviated
                if Arxiv[i].endswith(".") and \
                  Arxiv[i][:-1] == name[:len(Arxiv[i])-1]:
                    return True
                elif Arxiv[i] == name[:len(Arxiv[i])]:
                    return True
    return False


# CAS first names list and CAS surname list are used to find if the arxiv name
# matches any potential CAS authors.
def full_name_search(CAS_fname, CAS_sname, arxiv_name, student):
    arxiv_split = np.array(arxiv_name.split())
    for i in range(len(CAS_sname)):
        if student[i] is True:
            is_student = True
        else:
            is_student = False
        sname_split = np.array(CAS_sname[i].split())
# Surname match
        if name_match(sname_split, arxiv_split, last_name=True) is True:
            fname_split = np.array(CAS_fname[i].split())
# First name match
            if name_match(fname_split, arxiv_split) is True:
                return True, is_student
    return False, False


###############################################################################
#                             Check for new papers                            #
###############################################################################
if __name__ == '__main__':
    journal_list = np.array(  # list of journals, expand if needed
            ['MNRAS', 'Monthly Notices of the Royal Astronomical Society',
             'ApJS', 'Astrophysical Journal Supplement Series',
             'ApJL', 'Astrophysical Journal Letters',
             'ApJ', 'Astrophysical Journal',
             'ARAA', 'Annual Review of Astronomy and Astrophysics',
             'A&A', 'Astronomy & Astrophysics',
             'PASA', 'Publications of the Astronomical Society of Australia',
             'Nature', 'Science', 'Physics of Plasmas',
             'RNAAS', 'Planetary Science Journal', 'Astronomical Journal',
             'AJ', 'RPD', 'JGR', 'Icarus', 'Astronomy Letters'])

# needed for splitting
    alphabet = 'q|w|e|r|t|y|u|i|o|p|l|k|j|h|g|f|d|s|a|z|x|c|v|b|n|m'

    print('Checking for new papers:')
    print("----------")

# read in names from a file
    file_path = "List_of_authors.csv"
    first_name, last_name, student = csv_file_to_names(file_path)

# clean up accents and hyphens in names
    first_name = remove_accents_array(first_name)
    last_name = remove_accents_array(last_name)
    first_name = remove_hyphens(first_name)
    last_name = remove_hyphens(last_name)
    for i, string in enumerate(student):
        student[i] = string.startswith('Student')

# institute
    institute = 'SwinburneUniversity'

# read URL content
#    URL = 'https://arxiv.org/list/astro-ph/new'
    URL = 'https://arxiv.org/list/astro-ph/pastweek?show=1000'

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

# get info from webpage
    results = soup.find(id="dlpage")
    authors = results.find_all("div", class_="list-authors")
    pdf_links = results.find_all("span", class_="list-identifier")

# get arXiv ids to obtain pdfs
    ArxivIDs = [str(i).split('/abs/')[1].split('"')[0] for i in pdf_links]

# create lists for authors -> have to do this nicer somehow...
    List_other_authors_idx = []
    All_authors = []
    for N_paper, author in enumerate(authors):
        AofPap = author.text

        Other_Authors = AofPap.split('\n')[2:]

# if there are authors not shown on the arXiv
        no_hidden_authors = True
        for i in Other_Authors[-5:]:
            if 'additional authors not shown' in i:
                no_hidden_authors = False
                search = arxiv.Search(id_list=[ArxivIDs[N_paper]])

                for result in search.results():
                    Authors = result.authors

                for author_names in Authors:
                    List_other_authors_idx.append(N_paper)
                    All_authors.append(author_names.name)

        if no_hidden_authors:
            for i in range(len(Other_Authors)-1):
                Author = Other_Authors[i].split(',')[0]
                Author = Author.split(' (')[0]

                List_other_authors_idx.append(N_paper)
                All_authors.append(Author)

# clean up arXiv author names
    All_authors = remove_accents_array(All_authors)
    All_authors = remove_hyphens(All_authors)

# convert to array for later indexation
    List_other_authors_idx = np.array(List_other_authors_idx)

# Check for each arXiv author if there is a corresponding CAS author
# Note that one matching last name (full) and one matching first name (full or
# abbreviated in any way) will be enough to trigger the search for the CAS
# affiliation in the arXiv pdf.
    ind = []
    ind_student = []
    Aname = []
    for i, name in enumerate(All_authors):
        found_names, is_student = full_name_search(first_name, last_name, name,
                                                   student)
        if found_names is True:
            ind = np.append(ind, List_other_authors_idx[i])
            ind_student.append(is_student)
            Aname.append(name)
# i is the index under which to find selected authors
# i.e. All_authors[i] are selected authors

    unique_ids = np.unique(ind)  # get unique paper ids to remove duplicates

# check aff for each paper
    for i in unique_ids:
        ArxivID = ArxivIDs[int(i)]  # get arXiv id of paper
# get names of potential swinburne authors
        SwinAuth = np.array(Aname)[ind == i]
# Check for student
        student_status = np.array(ind_student)[ind == i]
# check institution
        check_institute(ArxivID, institute, SwinAuth, student_status)

    print('done')
