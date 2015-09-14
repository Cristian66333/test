#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import os       # for getting files from directory
import operator # for sorting data with multiple keys

# XML results files location (modify as needed):
folder_name = "../saves"    # Looks in 'saves/' folder from 'scripts/' folder

# Turn number of seconds (int) to '[minutes] min [seconds] s' (string)
def seconds2timestr(time_in_seconds):
    time_in_minutes = int(time_in_seconds/60)
    remaining_seconds = int(time_in_seconds%60)
    return str(time_in_minutes) + " min " + str(remaining_seconds) + " s"

# stats initialisation
number_of_XML_files  = 0
number_of_pages      = 0
number_of_fragments  = 0
total_empty_comments = 0
time_per_page_accum  = 0

# arrays initialisation
page_names       = []
page_count       = []
duration_page    = []      # duration of experiment in function of page content
duration_order   = []      # duration of experiment in function of page number
fragments_per_page = []    # number of fragments for corresponding page

# get every XML file in folder
files_list = os.listdir(folder_name)
for file in files_list: # iterate over all files in files_list
    if file.endswith(".xml"): # check if XML file
        number_of_XML_files += 1
        tree = ET.parse(folder_name + '/' + file)
        root = tree.getroot()
        
        print file # print file name (subject name)
        
        # reset for new subject
        total_duration = 0
        page_number = 0
        
        # get list of all page names
        for audioholder in root.findall("./audioholder"):   # iterate over pages
            page_name = audioholder.get('id')               # get page name
            
            if page_name is None: # ignore 'empty' audio_holders
                print "WARNING: " + file + " contains empty audio holder. (evaluation_stats.py)"
                break # move on to next
            
            number_of_comments = 0 # for this page
            number_of_missing_comments = 0 # for this page
            
            # number of audio elements
            audioelements = audioholder.findall("./audioelement") # get audioelements
            number_of_fragments += len(audioelements) # add length of this list to total
            
            # number of comments (interesting if comments not mandatory)
            for audioelement in audioelements:
                response = audioelement.find("./comment/response")
                if response.text is not None and len(response.text) > 1: 
                    number_of_comments += 1
                else: 
                    number_of_missing_comments += 1
                    
            total_empty_comments += number_of_missing_comments
            
            # 'testTime' keeps total duration: subtract time so far for duration of this audioholder
            duration = float(audioholder.find("./metric/metricresult[@id='testTime']").text) - total_duration
            
            # total duration of test
            total_duration += duration
            
            # print audioholder id and duration
            print "    " + page_name + ": " + seconds2timestr(duration) + ", "\
                  + str(number_of_comments)+"/"\
                  +str(number_of_comments+number_of_missing_comments)+" comments"
            
            # keep track of duration in function of page index
            if len(duration_order)>page_number:
                duration_order[page_number].append(duration)
            else:
                duration_order.append([duration])
                
            # keep list of audioholder ids and count how many times each audioholder id
            # was tested, how long it took, and how many fragments there were (if number of 
            # fragments is different, store as different audioholder id)
            if page_name in page_names: 
                page_index = page_names.index(page_name) # get index
                # check if number of audioelements the same
                if len(audioelements) == fragments_per_page[page_index]: 
                    page_count[page_index] += 1
                    duration_page[page_index].append(duration)
                else: # make new entry
                    alt_page_name = page_name+"("+str(len(audioelements))+")"
                    if alt_page_name in page_names: # if already there
                        alt_page_index = page_names.index(alt_page_name) # get index
                        page_count[alt_page_index] += 1
                        duration_page[alt_page_index].append(duration)
                    else: 
                        page_names.append(alt_page_name)
                        page_count.append(1)
                        duration_page.append([duration])
                        fragments_per_page.append(len(audioelements))
            else: 
                page_names.append(page_name)
                page_count.append(1)
                duration_page.append([duration])
                fragments_per_page.append(len(audioelements))
                
            # bookkeeping
            page_number += 1 # increase page count for this specific test
            number_of_pages += 1 # increase total number of pages
            time_per_page_accum += duration # total duration (for average time spent per page)

        # print total duration of this test
        print "    TOTAL: " + seconds2timestr(total_duration)


# PRINT EVERYTHING

print "Number of XML files: " + str(number_of_XML_files)
print "Number of pages: " + str(number_of_pages)
print "Number of fragments: " + str(number_of_fragments)
print "Number of empty comments: " + str(total_empty_comments)
print "Average time per page: " + seconds2timestr(time_per_page_accum/number_of_pages)
page_count_strings = list(str(x) for x in page_count)
count_list = page_names + page_count_strings
count_list[::2] = page_names
count_list[1::2] = page_count_strings
print "Pages tested: " + str(count_list)

# Average duration for first, second, ... page
for page_number in range(len(duration_order)): 
    print "Average duration page " + str(page_number+1) + ": " +\
        seconds2timestr(sum(duration_order[page_number])/len(duration_order[page_number])) +\
            " ("+str(len(duration_order[page_number]))+" subjects)"


# Sort pages by number of audioelements, then by duration

# average duration and number of subjects per page
average_duration_page = []
number_of_subjects_page = []
for line in duration_page:
    number_of_subjects_page.append(len(line))
    average_duration_page.append(sum(line)/len(line))

# combine and sort in function of number of audioelements and duration
combined_list = [page_names, average_duration_page, fragments_per_page, number_of_subjects_page]
combined_list = sorted(zip(*combined_list), key=operator.itemgetter(1, 2)) # sort

# Show average duration for all songs
for page_index in range(len(page_names)):
    print "Average duration audioholder " + combined_list[page_index][0] + ": " \
          + seconds2timestr(combined_list[page_index][1]) \
          + " (" + str(combined_list[page_index][3]) + " subjects, " \
          + str(combined_list[page_index][2]) + " fragments)"


#TODO
# time per page in function of number of fragments (plot)
# time per participant in function of number of pages
# plot total time for each participant
# plot total time
# show 'count' per page (in order)

# clear up page_index <> page_count <> page_number confusion