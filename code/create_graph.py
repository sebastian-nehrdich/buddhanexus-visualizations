import sys
import json 
import re
import networkx as nx
import gzip
import multiprocessing
import os 


import matplotlib.pyplot as plt

from utils import test_if_should_add, populate_filenamedic


lang = "skt"
min_length = 10
do_cooc_smoothing = False
metadata_path = ""
match_data_path = ""
number_of_threads = 24
output_path = "../output/" + lang + ".gexf"


do_mst = False # if true, use minimum spanning tree to find the best path

include_regex = ["^T"] #["1558","1586","1590","1609","1586","1600","1597","1612"]
exclude_regex = [] #["X"] 

if lang == "chn":
    metadata_path = "../metadata/chn-files.json"
    match_data_path = "../data/chn/"
if lang == "pli":
    metadata_path = "../metadata/pli-files.json"
    match_data_path = "../data/pli/"
if lang == "skt":
    metadata_path = "../metadata/skt-files.json"
    match_data_path = "../data/skt/"
if lang == "tib":
    metadata_path = "../metadata/tib-files.json"
    match_data_path = "../data/tib/"


def test_match_by_content(content):
    "you can leave conditions here to exclude certain matches"
    #if not "玄奘" in content:
    return True

filenames = populate_filenamedic(metadata_path)
    
def rename_segment(segment):
    textname,position = segment.split(":")
    textname = re.sub("_.*", "", textname).strip()
    if textname in filenames:
        full_name = filenames[textname]
        return full_name
    else:
        print("ERROR: could not find",textname)
        return textname
     

def process_folder(path, number_of_threads):
    filelist = []
    lengths = {}
    results = []
    for file in os.listdir(path):        
        filename = os.fsdecode(file)        
        if test_if_should_add(filename, include_regex, exclude_regex):
            filelist.append(path+filename)
    pool = multiprocessing.Pool(processes=number_of_threads)
    results = pool.map(process_file,filelist)
    pool.close()
    lengths = {}
    final_results = {}
    for result in results:
        current_results,current_lengths = result
        lengths.update(current_lengths)
        final_results.update(current_results)
    create_graph(final_results,lengths)    

def process_file(current_file):
    print("NOW PROCESSING FILE",current_file)
    lengths = {}
    results = {}
    current_file = json.load(gzip.open(current_file,"rb"))
    segments = current_file[0]
    # first we collect the lengths
    for segment in segments:
        current_filename = rename_segment(segment['segnr'])
        current_length = len(segment['segtext'])
        if current_filename not in results:
            results[current_filename] = {}
        if current_filename in lengths:
            lengths[current_filename] += current_length
        else:
            lengths[current_filename] = current_length
            
    matches = current_file[1]
    # we need to build this dic to speedup the cooc search

    for match in matches:
        master_filename = rename_segment(match['root_segnr'][0])
        par_filename = rename_segment(match['par_segnr'][0])
        score = match['par_length']
        if do_cooc_smoothing:
            cooc = match['co-occ']
            score = score / cooc
        if test_if_should_add(match['par_segnr'][0], include_regex, exclude_regex) and match['par_length'] > min_length:
            if test_match_by_content(match['par_string']) and master_filename != par_filename:
                if master_filename in results:
                    if par_filename in results[master_filename]:
                        results[master_filename][par_filename] += score
                    else:
                        results[master_filename][par_filename] = score
                else:
                    results[master_filename] = {}
                    results[master_filename][par_filename] = score
    return [results,lengths]



def create_graph(collected_stats,lengths):
    global g
    g = nx.MultiGraph()
    idcount = 0 
    print("Creating graph")
    for master_file in collected_stats:
        g.add_node(master_file)
        current_results = collected_stats[master_file]
        for quoted_file in current_results:
            g.add_node(quoted_file)
            score = current_results[quoted_file]
            length_master = lengths[master_file]            
            weight = (score/length_master)            
            g.add_edge(master_file,quoted_file,weight=weight,key=idcount)
            idcount += 1
    print("Finished creating graph")
    if do_mst:
        print("Calculating MST")
        g = nx.algorithms.tree.mst.maximum_spanning_tree(g)
        print("Finished calculating MST")    
    nx.write_gexf(g, output_path)                 
    

                       
                
process_folder(match_data_path, number_of_threads)


