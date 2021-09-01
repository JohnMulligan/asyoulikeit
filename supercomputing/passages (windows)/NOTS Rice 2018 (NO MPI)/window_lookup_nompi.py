import sqlite3
import argparse
from collections import OrderedDict
import time
'''from mpi4py import MPI
import signal'''
import os
import re
parser = argparse.ArgumentParser(description='start and end lines for calculation.')
#parser.add_argument('start_line', type=int,default=1)
#parser.add_argument('end_line', type=int,default=3153)
parser.add_argument('window_size',type=int,default=10)
parser.add_argument('results_count',type=int,default=20)

args = parser.parse_args()

window_size = args.window_size
results_count = args.results_count
'''comm = MPI.COMM_WORLD
rank = comm.rank
size = comm.size
status = MPI.Status()'''

#first try for checkpointed ranges
#then go for the master ranges
try:
	d = open('play_boundary_unfinished-%s-%s' %(str(window_size),str(results_count)),'r')
	t = d.read()
	play_boundary_entries = t.split('\n')
	d.close()
except:
	d = open('play_boundary.csv','r')
	t=d.read()
	play_boundary_entries = t.split('\n')
	d.close()

'''interrupted = False
#code from http://www.cism.ucl.ac.be/Services/Formations/checkpointing.pdf
def signal_handler(signum, frame):
	global interrupted
	interrupted = True
	
signal.signal(signal.SIGINT, signal_handler)'''

print args

def create_database(proc_play,start_line,end_line):
	
	dbname = "ariel_windowsize-%s_resultscount-%s_play-%s.db" %(str(window_size),str(results_count),proc_play)
	check = os.listdir('.')
	if dbname not in check:
		new_cnx = sqlite3.connect(dbname)
		new_cursor = new_cnx.cursor()

		target_string = ''
		for i in range(1,results_count+1):
			target_string += ',target%d_id int,count%d int' %(i,i)
	
		tables = []
	
		tables.append("CREATE TABLE matches (source_id int PRIMARY KEY%s);" %target_string)
		tables.append("CREATE TABLE docs (source_id int,target_id int,docs text,PRIMARY KEY(source_id,target_id));")
	
		for table in tables:
			new_cursor.execute(table)
			new_cnx.commit()
		new_cnx.close()
	else:
		#if the database already exists, then there should be a checkpointing file
		d = open("checkpoint-%s-%s-%s" %(proc_play,str(window_size),str(results_count)))
		start_line = int(d.read())
		d.close()
	return dbname,start_line


def main(newdb,proc_play,start_line,end_line):
	cnx = sqlite3.connect("/mnt/rdf/shakespeare/windows/ariel_reduced.db")
	cursor = cnx.cursor()
	play_boundary_entries = cursor.execute("SELECT play,startline_id,endline_id FROM play_boundary;").fetchall()
	play_boundaries = {i[0]:[i[1],i[2]] for i in play_boundary_entries}
	
	new_cnx = sqlite3.connect(newdb)
	new_cursor = new_cnx.cursor()

	window = {}

	window_dictionary = {}

	starttime = time.time()
	source_play = proc_play
	source_play_boundaries = play_boundaries[source_play]
	
	for line_id in range(start_line,end_line+1):
		

		startlooptime = time.time()
		
		if source_play_boundaries[1]-line_id < window_size:
			this_window = range(source_play_boundaries[1]-window_size+1,source_play_boundaries[1]+1)
		else:
			this_window = range(line_id,line_id+window_size)
		
		print "this window: %s" %str(this_window)
	
		new_entries = [i for i in this_window if i not in window_dictionary.keys()]
		outside = [i for i in window_dictionary.keys() if i not in this_window]
	
		for i in outside:
			del window_dictionary[i]
	
		for i in new_entries:
		
			new_scored_matches = get_scored_matches(i,cursor,source_play_boundaries)
		
			window_dictionary[i] = new_scored_matches
	
		scored_target_windows = {}
		window_source_lines = window_dictionary.keys()
		for source_line in window_source_lines:
			target_lines = window_dictionary[source_line].keys()
			
			for target_line in target_lines:
				
				target_play = get_play(target_line,play_boundaries)
				target_play_boundaries = play_boundaries[target_play]
		
				if target_play_boundaries[1]-target_line <= window_size:
					nominal_target_line = target_play_boundaries[1] - window_size
					#print target_line, nominal_target_line
				else:
					nominal_target_line = target_line
				c=0
				score = 0
				articles = []
				while c < window_size:
					try:
						score += window_dictionary[source_line][nominal_target_line+c][0]
						articles.append(window_dictionary[source_line][nominal_target_line+c][1])
					except:
						pass

					c+=1
				
				try:
					known_score,known_articles = scored_target_windows[nominal_target_line]
					
					new_score = known_score + score
					new_articles = known_articles + articles
					scored_target_windows[nominal_target_line] = [new_score,new_articles]
				except:
					scored_target_windows[nominal_target_line] = [score,articles]

		#print scored_target_windows
		top_matches = {}
	
		#prev_entry_play = ''
		#prev_entry_id=1000000
				
		for candidate in sorted(scored_target_windows.items(), key=lambda t: t[1][0], reverse=True):
		
			#record the top scored matches as long as these don't overlap (that is, are within the window size)
			#the selection is therefore somewhat arbitrary -- we have a lot of large-windowed same-scored matches -- I just record the first one we hit
			candidate_play = get_play(candidate[0],play_boundaries)
			
			made_matches = top_matches.keys()

			close_made_matches_plays = [get_play(i,play_boundaries) for i in made_matches if abs(candidate[0]-i) < window_size]
			
			if (candidate_play not in close_made_matches_plays) or len(close_made_matches_plays) == 0:
				top_matches[candidate[0]] = candidate[1]
		   
			if len(top_matches.keys()) >= results_count:
				break
		
		target_string_cols=''
		target_string_vals=''
		c=1

		
		if len(top_matches.keys())>0:
			for match in sorted(top_matches.items(), key=lambda t: t[1][0], reverse=True):
			
			
				target_id = match[0]
				count = match[1][0]
				docs = list(set(match[1][1]))
				docs_str = str(docs)[1:-1]
				new_cursor.execute("INSERT OR IGNORE INTO docs(source_id,target_id,docs) VALUES(%s,%s,'%s');" %(str(line_id),str(target_id),docs_str))
				target_string_cols += 'target%d_id,count%d,' %(c,c)
				target_string_vals += '%d,%d,' %(target_id,count)
				c+=1
		
			target_string_cols = target_string_cols[0:-1]
			target_string_vals = target_string_vals[0:-1]
		
			new_cursor.execute("INSERT OR IGNORE INTO matches(source_id,%s) VALUES (%s,%s);" %(target_string_cols,str(line_id),target_string_vals))
		
			new_cnx.commit()
	
		print "loop time = %s" %str(round(time.time()-startlooptime))
		
		d=open("checkpoint-%s-%s-%s" %(proc_play,str(window_size), str(results_count)),"w")
		d.write('%d' %(line_id+1))
		d.close()
		
		
	if line_id == end_line:
		print 'play=%s completed in %s seconds' %(proc_play,str(round(time.time()-starttime)))
		
def get_play(line_id,play_boundaries):
	
	##print "fetching play for line_id %d" %line_id
	##print play_boundaries
	this_play = [play for play in play_boundaries.keys() if line_id >= play_boundaries[play][0] and line_id <= play_boundaries[play][1]][0]
	return this_play


def get_scored_matches(line_id,cursor,play_boundaries):
	#print "fetching matches on source line %d" %line_id
	
	lower,upper = play_boundaries
	results = cursor.execute("SELECT source_line_id,target_line_id,doc_id FROM lines_and_docs_matches WHERE (source_line_id = %d OR target_line_id = %d) AND ((source_line_id NOT BETWEEN %d AND %d) OR (target_line_id NOT BETWEEN %d AND %d));" %(line_id,line_id,lower,upper,lower,upper)).fetchall()
	matches = {}
	for result in results:
		nonself = [i for i in result[0:2] if i != line_id][0]
		
		try:
			matches[nonself][0] += 1
			matches[nonself][1].append(result[2])
			
		except:
			matches[nonself] = [1,result[2]]
	#print "found %d matches" %len(matches.keys())
	
	return matches

if __name__ == "__main__":
    proc_play,start_line,end_line = play_boundary_entries[0].split(',')
    newdb,start_line = create_database(proc_play,start_line,end_line)

    start_line = int(start_line)
    end_line = int(end_line)

    main(newdb,proc_play,start_line,end_line)

	
