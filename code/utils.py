import json 
import re

def test_if_should_add(filename, regex_tests_positive, regex_tests_negative):    
    regex_test_pos = '|'.join(regex_tests_positive)    
    regex_test_neg = '|'.join(regex_tests_negative)
    add_flag = False
    if re.search(regex_test_pos,filename):
        add_flag = True        
    if re.search(regex_test_neg,filename) and len(regex_tests_negative) > 0:
        add_flag = False
    return add_flag 

def populate_filenamedic(path):
    namedic = {}
    file_data = json.load(open(path,'rb'))
    for entry in file_data:
        filename = entry['filename'].split('_')[0]
        namedic[filename] = entry['displayName'] + "\n (" + entry['textname'] + ")"
    return namedic



# this function is necessary to weight down matches with a high tendency of co-occurrence! 
def get_coocurrence(cmatch,match_dict):
    # build a dict first to avoid slow loops
    cmatch_pos_beg = cmatch['root_pos_beg']
    cmatch_length = cmatch['par_length']
    allowed_variation = cmatch_length * 0.2
    cooccurrence = 1
    cmatch_segments = cmatch['root_segnr']
    matches_to_check = []
    for segment in cmatch_segments:
        matches_to_check.extend(match_dict[segment])
    for pmatch in matches_to_check:
        if cmatch['par_segnr'] != pmatch['par_segnr'] and pmatch['par_length'] > min_length and pmatch['root_length'] > min_length: # make sure to not check the same match
            pmatch_pos_beg = pmatch['root_pos_beg']
            if abs(cmatch_pos_beg-pmatch_pos_beg) < 3: # It is important to know that this variable is operating on token-level!
                pmatch_length = pmatch['par_length'] 
                if abs(cmatch_length-pmatch_length) < allowed_variation:
                    cooccurrence += 1
    return cooccurrence / 2