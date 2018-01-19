import numpy as np
import re
import string
import pandas as pd
from names import clean_string, alternative_name_list
import urllib2
import time
from pync import Notifier
import logging


def get_data_from_page(page, data=None):
    if data == None:
        data = []
    j = re.findall('<tr class="row.".*instcol">(?P<School>[\w, \s]*)'
                   '</td><td>(?P<Program>[\w, \s, (,)]*)'
                   '</td><td><span class="\w*">(?P<Result>[\w]*)<'
                   '.*on\s(?P<Result_Date>[\w, \s]*)\s'
                   '(?:.*GPA</strong>:\s(?P<GPA>[\w, /,.]*)<)?'
                   '(?:.*V/Q/W.*</strong>:\s(?P<Verbal_GRE>[\d]*)/(?P<Quantitative_GRE>[\d]*)/(?P<Writing_GRE>[\d, .]*))?'
                   '(?:.*Subject.*:\s(?P<Subject_GRE>[/,\w]*))?'
                   '(?:.*diams;</a></td><td>(?P<Status>\w)<)?'
                   '.*datecol">(?P<Submitted_Date>[\w, \s]*)', page)
    for group in j:
        data.append(group)
    return data


def get_page(i=0, keyword="computer%20science"):
    time.sleep(1)
    if i == 0:
        url = "http://thegradcafe.com/survey/index.php?q=" + keyword + "*&t=a&o=&pp=250"
    else:
        url = "http://thegradcafe.com/survey/index.php?q=" + \
            keyword + "*&t=a&pp=250&o=&p=" + str(i)
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    response = opener.open(url)
    html = response.read()
    return html


def find_n_pages():
    html = get_page()
    reg = re.search('over\s([\d]*)\spages', html)
    return int(reg.groups()[0])


def get_pages(n_max):
    n = find_n_pages()
    if n_max is not None:
        logging.info("Total pages: %d" % n)
        n = min(n, n_max)
    logging.info("Getting %d pages." % n)

    pages = []
    for i in range(1, n + 1):
        logging.info("Getting page %d" % i)
        pages.append(get_page(i))
    return pages


def get_data(n_max=None):
    data = []
    pages = get_pages(n_max)
    for page in pages:
        data = get_data_from_page(page, data)
    return data


def clean(x, kind='float'):
    if (x == '')or(x == 'n/a'):
        return np.NaN
    else:
        if kind == 'float':
            return float(x)
        elif kind == 'str':
            return str(x)


def substrings_in_string(big_string, substrings):
    for substring in substrings:
        if string.find(big_string, substring) != -1:
            return substring

    # print big_string
    return 'Other'


def degree_type(x):
    if (x == 'PhD')or(x == 'PHD'):
        return 'Phd'
    elif (x == 'Masters')or(x == 'MS'):
        return 'Masters'
    else:
        return x


def get_dataframe(n_max):
    data = get_data(n_max)
    df = pd.DataFrame(data)
    colnames = ['School', 'Program', 'Result', 'Result_Date', 'GPA',
                'Verbal_GRE', 'Quant_GRE', 'Writing_GRE',
                'Subject_GRE', 'Status', 'Submit_Date']

    df.columns = colnames
    df['GPA'] = df['GPA'].map(clean)
    df['Verbal_GRE'] = df['Verbal_GRE'].map(clean)
    df['Subject_GRE'] = df['Subject_GRE'].map(clean)
    df['Writing_GRE'] = df['Writing_GRE'].map(clean)
    df['Quant_GRE'] = df['Quant_GRE'].map(clean)
    df['Status'] = df['Status'].map(lambda x: clean(x, kind='str'))

    degree_types = ['PhD', 'PHD', 'Masters', 'MS']
    df['Degree_Type'] = df['Program'].map(lambda x: substrings_in_string(x,
                                                                         degree_types))
    df['Degree_Type'] = df['Degree_Type'].map(degree_type)

    # Changing Data Types
    df['Submit_Date'] = pd.to_datetime(df['Submit_Date'])
    df['Result_Date'] = pd.to_datetime(df['Result_Date'])

    return df
