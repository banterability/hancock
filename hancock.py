# Stdlib imports
import datetime
import re

# 3rd Party imports
from lxml import etree

# Package imports
from parser import parse
from load import get_results

def fetch(download_url, data_file="X10GG_510.xml", tmp_dir="election_tmp"):
    """
    Return tuple with retrieval time and parsed election results.
    
    Arguments:
    - DOWNLOAD_URL: URL where election results are posted
    - DATA_FILE: File inside zip package to parse (full results XML)
    - TMP_DIR: Temporary working directory on local filesystem
    """
    # Download results file and extract XML
    response = get_results(download_url, data_file, tmp_dir)
    
    # Create ElenentTree object from XML
    results = etree.fromstring(response)
    
    # Get all _Contest_ objects from results
    contests = results.findall('.//Contests/Contest')
    
    # Parse update time string to native `DateTime` object
    update_time = result_date = datetime.datetime(*map(int, re.split('[^\d]', results.findtext("IssueDate"))[:-1])) 
    return (update_time, parse(contests))