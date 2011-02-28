# Maps the first four digits of an contest ID to related
# descriptions and race types.
#
# _Source: [Election Night Date Feed User Guide](http://www.sos.ca.gov/media/10gg/election-night-data-feed-user-guide-v4.0.pdf), p.71-73_
#
CONTEST_TYPES = {
    '0200': {'description': 'Governor', 'type': 'candidate'},
    '0300': {'description': 'Lieutenant Governor', 'type': 'candidate'},
    '0400': {'description': 'Secretary of State', 'type': 'candidate'},
    '0500': {'description': 'State Controller', 'type': 'candidate'},
    '0600': {'description': 'State Treasurer', 'type': 'candidate'},
    '0700': {'description': 'Attorney General', 'type': 'candidate'},
    '0800': {'description': 'Insurance Commissioner', 'type': 'candidate'},
    '0900': {'description': 'Board of Equalization', 'type': 'candidate'},
    '1000': {'description': 'U.S. Senate', 'type': 'candidate'},
    '1100': {'description': 'U.S. Representative in Congress', 'type': 'candidate'},
    '1200': {'description': 'State Senate', 'type': 'candidate'},
    '1300': {'description': 'State Assembly', 'type': 'candidate'},
    '1400': {'description': 'Supreme Court Justices', 'type': 'measure'},
    '1500': {'description': 'Courts of Appeal Justices', 'type': 'measure'},
    '1600': {'description': 'Superintendent of Public Instruction', 'type': 'candidate'},
    '1900': {'description': 'Ballot Measures', 'type': 'measure'},
}

#### Helper functions

# ===Handles races with a number of candidates===
def process_candidate(contest_package):
    """
    Handle a contest with candidates.
    """
    contest = contest_package["contest"]
    
    # Get precinct progress data
    precinct_count = contest.findtext("TotalVotes/CountMetric[@Id='PR']")
    precinct_total = contest.findtext("TotalVotes/CountMetric[@Id='TP']")
        
    # Find all available candidates
    selections = contest.findall('TotalVotes/Selection')
    choices = []
    total_votes = 0
    
    for s in selections:
        cid = s.find("Candidate/CandidateIdentifier").get("Id")
        cname = s.findtext("Candidate/CandidateIdentifier/CandidateName")

        # Get candidate's party affiliation
        cparty = s.findtext("Candidate/Affiliation/Type")
        
        # Get candidate's incumbency status
        if s.find("AffiliationIdentifier[@Id='Incumbent']") is not None:
            is_incumbent = True
        else:
            is_incumbent = False
        
        # Get candidate's vote count & add to total votes
        votes = s.findtext("ValidVotes")
        total_votes += int(votes)
        
        # Get candidate's percentage of vote in this contest
        pv = s.findtext("CountMetric[@Id='PVR']")
        
        # Add `dict` of candidate data to list for this contest
        choices.append({
            cid: {
                'votes': int(votes),
                'percent': pv,
                'is_incumbent': is_incumbent,
                'party': cparty,
                'name': cname,
                }
        })
    
    results = {
        'contest_name': contest_package['name'],
        'contest_id': contest_package['id'],
        'contest_description': contest_package["info_dict"]["description"],
        'contest_type': contest_package["info_dict"]["type"],
        'total_votes': total_votes,
        'choices': choices, # list of candidate `dict`'s
        'precincts_reporting': precinct_count,
        'total_precincts': precinct_total
    }
    return results

# ===Handles races with yes/no options===
def process_measure(contest_package):
    """
    Handle a contest with yes/no options.
    """
    contest = contest_package["contest"]

    # Get precinct progress data
    precinct_count = contest.findtext("TotalVotes/CountMetric[@Id='PR']")
    precinct_total = contest.findtext("TotalVotes/CountMetric[@Id='TP']")
    
    # Get percentage of yes & no votes in this contest
    pyv = contest.findtext('TotalVotes/CountMetric[@Id="PYV"]')
    pnv = contest.findtext('TotalVotes/CountMetric[@Id="PNV"]')

    # Get all available responses (Should just be yes and no)
    selections = contest.findall('TotalVotes/Selection')
    
    total_votes = 0
    # __TODO__: Shouldn't loop & manually check identifier. One or the other please.
    for s in selections:
        cname = s.find("Candidate/ProposalItem").get("ReferendumOptionIdentifier")
        votes = s.findtext("ValidVotes")
        total_votes += int(votes)
        
        # Check option identifier and associate with vote percentages
        if cname == "Yes":
            yes_percent = pyv
            yes_votes = votes
        elif cname == "No":
            no_percent = pnv
            no_votes = votes
        else:
            raise
    
    results = {
        'contest_name': contest_package['name'],
        'contest_id': contest_package['id'],
        'contest_description': contest_package["info_dict"]["description"],
        'contest_type': contest_package["info_dict"]["type"],
        'total_votes': total_votes,
        'choices': [
            {'yes': {'votes': int(yes_votes), 'percent': yes_percent}},
            {'no': {'votes': int(no_votes), 'percent': no_percent}}
        ],
        'precincts_reporting': precinct_count,
        'total_precincts': precinct_total
    }
    return results

#### Processing the races

# ===Performs type detection on contests and passes them through appropriate helper function===
def parse(contests):
    """
    Returns list of dictionaries containing results for each contest
    """
    results = []
    for contest in contests:
        # Extract the contest ID and compare against knwon types
        contest_id = contest.find('ContestIdentifier').get("Id", "Not defined")
        contest_type_dict = CONTEST_TYPES[contest_id[0:4]]
        
        contest_type = contest_type_dict["type"]

        # Package contest plus previously accessed data for helper functions
        contest_package = {
            'contest': contest,
            'id': contest_id,
            'info_dict': contest_type_dict,
            'name': contest.findtext('ContestIdentifier/ContestName')}
        
        # Hand off contest to helper function based on type
        if contest_type == "measure":
            results.append(process_measure(contest_package))
        elif contest_type == "candidate":
            results.append(process_candidate(contest_package))
        else:
            # Fail loudly if an unknown type appears
            raise
    return results
    