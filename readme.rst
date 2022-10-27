Centre for Astronomy and Supercomputing coding challenge entry
==============================================================
This is the entry of Geray Karademir (https://github.com/GKarademir) and Christian Lehmann (https://github.com/CLehmann94) in the CAS Coding Challenge. It uses a list of authors as input and finds paper publications of all those authors on https://arxiv.org/archive/astro-ph (can be changed within the code to other ArXiv fields).

This software is meant to be run by a system that executes it regularly (i.e. daily, weekly or monthly) and feeds it into a table or a weekly email. This is meant to celebrate the achievements of astronomers in the centre. 


Usage
-----
The algorithm is meant to be part of an automated system that fetches the publication information regularly, but it can be executed from within a python (3.7 or later) environment with the neccessary dependencies (see below)::

  $ python3 CAS_coding_challenge.py

Note that it accesses a list of authors to be identified on the ArXiv ("List_of_authors.csv"), which only contains the authors of this document and Prof. Murphy as an examle array of publishing authors.


Output
------
Title: the titel of the publication

Centre for Astronomy and Supercomputing coding challenge entry
==============================================================
This is the entry of Geray Karademir (https://github.com/GKarademir) and Christian Lehmann (https://github.com/CLehmann94) in the CAS Coding Challenge. It uses a list of authors as input and finds paper publications of all those authors on https://arxiv.org/archive/astro-ph (can be changed within the code to other ArXiv fields).

This software is meant to be run by a system that executes it regularly (i.e. daily, weekly or monthly) and feeds it into a table or a weekly email. This is meant to celebrate the achievements of astronomers in the centre. 


Usage
-----
The algorithm is meant to be part of an automated system that fetches the publication information regularly, but it can be executed from within a python (3.7 or later) environment with the necessary dependencies (see below)::

  $ python3 CAS_coding_challenge.py

Note that it accesses a list of authors to be identified on the ArXiv ("List_of_authors.csv"), which only contains the authors of this document and Prof. Murphy as an example array of publishing authors.


Output
------
Title: the title of the publication

ArXiv: the access link to the publication abstract

Authors: all authors of the paper (including those not in the list of authors)

CAS Affiliates: all authors affiliated with the Centre for Astronomy and Supercomputing at Swinburne University (Note that this can be changed in the code if desired)

Status: the status of the publication with regard to the journal. Possible status: Submitted, Accepted, Published, unknown (if this information was not available)

Journal: the journal which the paper is submitted to (currently only checks for astrophysics/astronomy journals) 


Dependencies
------------
arxiv       1.4.2

beautifulsoup4  4.11.1

bs4        0.0.1

numpy       1.19.5

PyPDF2      2.11.1

pandas      1.1.5

requests     2.27.1

urllib3      1.26.12


The original challenge (Quoted from Prof. Michael Murphy, Swinburne University)
=========================================================
The challenge:

– Identify new papers on arXiv which include current (& recent former) CAS members as co-authors.

– Minimise false-positives/negatives by checking basic versions of CAS member names and identifying affiliation information.

– Serve basic paper information in a format (TBD) useful for a CAS-wide "noticeboard"/database, record and inclusion in the "At CAS this week" emails.

– A label showing submission status, where available, e.g. "Accepted", "Submitted", "Published" or "Unknown" (derived from the Comments field in arXiv, most likely).

– Preferably run each day & collated weekly.

– Preferably the database could be edited by CAS members to correct anything, delete false-positives, add false-negatives and add/update status if desired.
