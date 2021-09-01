##package installation instructions
####tar xzvf mysql-connector-python-2.1.7.tar
####cd mysql-connector-python-2.1.7
####sudo python setup.py clean
####(skipping over some unnecessary steps listed here: https://stackoverflow.com/questions/1448429/how-to-install-mysqldb-python-data-access-library-to-mysql-on-mac-os-x#1448476)
####sudo python setup.py build
####sudo python setup.py install
####
import sqlite3
from optparse import OptionParser, Option, OptionValueError
import re

def list_callback(option, opt, value, parser):
	setattr(parser.values, option.dest, value.split(','))

parser = OptionParser()
parser.add_option("-p", action="store", type="str", dest="p",)
parser.add_option("-t", action="store", type="str", dest="t", default=15)


(options, args) = parser.parse_args()

def retrieve_all(cur,parameter,table,expression):
	
	query="SELECT %s FROM %s WHERE %s" %(parameter, table, expression)

	cur.execute(query)
	
	result = cur.fetchall()
	
	return result



def build_play_lines_dictionary(play_act,threshold):
	#0. Get database instances
	cnx = sqlite3.connect('shakespeare.db')
	cnx2 = sqlite3.connect('%s.db' %play_act)
	dbdata(cnx2)
	
	#1. Get lines from play
	
	play_line_output = retrieve_all(cnx.cursor(),"line,ftln","play_lines","line LIKE '%s%%'" %(play_act))
	play_lines = [pl[0] for pl in play_line_output]
	cnx.cursor().close()
	
	line_play = re.sub("\.[0-9]","",play_act)
	print line_play
	
	#iterate over all the lines in the play to see what documents reference them
	for l in play_lines:
		line = l
		cursorA = cnx.cursor()
		cursorB = cnx2.cursor()
		
		matched_docs = retrieve_all(cursorA,"docid,id","matches","(line='%s' and match_size > %s);" %(line,str(threshold)))
		
		line_ftln = retrieve_all(cursorA,"ftln","play_lines","line = '%s'" %line)[0][0]
		
		source_line_id = retrieve_all(cursorB,"rowid","lines","line = '%s'" % line)
		
		if source_line_id == []:
			cursorB.execute("INSERT INTO lines (line,ftln,play) VALUES ('%s',%s,'%s')" %(line,line_ftln,line_play))
			cnx2.commit()
			source_line_id = retrieve_all(cursorB,"rowid","lines","line = '%s'" % line)[0][0]
		else:
			source_line_id = source_line_id[0][0]
		
		#iterate over the documents to see what other lines they link to
		
		print l
		
		if len(matched_docs) > 0:
			for matched_doc in matched_docs:
				
				doi = matched_doc[0]
				match_id = matched_doc[1]
				
				'''title,journal,pubyear,authors = retrieve_all(cursorA,"title,journal,pubyear,authors","articles","docid = '%s'" %doi)[0]'''
				
							
			
				#screen out self-references as you gather matches to this line through the documents
				line_matches = [i[0] for i in retrieve_all(cursorA,"line","matches","docid = '%s' and (match_size > %s and id != '%s')" %(doi,str(threshold),match_id))]
				
				#iterate over the line matches to create the match dataset
				for lm in line_matches:
					match_play,match_ftln = retrieve_all(cursorA,"play,ftln","play_lines","line = '%s'" %(lm))[0]
					
					
					target_line_id = retrieve_all(cursorB,"rowid","lines","line = '%s'" % lm)
					if target_line_id == []:
						cursorB.execute("INSERT INTO lines (line,ftln,play) VALUES ('%s',%s,'%s')" %(lm,match_ftln,match_play))
						target_line_id = retrieve_all(cursorB,"rowid","lines","line = '%s'" % lm)[0][0]
					else:
						target_line_id = target_line_id[0][0]
					
					nominal_source,nominal_target = sorted([source_line_id,target_line_id])
					
					match = retrieve_all(cursorB,"rowid,co_citation_count","line_to_line_matches","(source_line_id = %s AND target_line_id = %s)" % (nominal_source,nominal_target))
					
					if match == []:
						cursorB.execute("INSERT INTO line_to_line_matches (source_line_id,target_line_id,co_citation_count) VALUES (%s,%s,1)" %(nominal_source,nominal_target))
						output_match_id = retrieve_all(cursorB,"rowid","line_to_line_matches","(source_line_id = %s AND target_line_id = %s)" % (nominal_source,nominal_target))[0][0]
					else:
						output_match_id = match[0][0]
						match_count = int(match[0][1])
						cursorB.execute("UPDATE line_to_line_matches SET co_citation_count = %s WHERE (rowid = %s)" % (str(match_count +1),str(output_match_id)))
					
					
					cursorB.execute("INSERT INTO docs (doi) SELECT '%s' WHERE NOT EXISTS(SELECT 1 FROM docs WHERE doi = '%s')" %(doi,doi))
					doc_id = retrieve_all(cursorB,"rowid","docs","doi = '%s'" % (doi))[0][0]

					
					cursorB.execute("INSERT INTO doc_to_matches_matches (lines_match_id,doc_id) VALUES (%s,%s)" %(str(output_match_id),str(doc_id)))
					cnx2.commit()
	
		cursorA.close()
		cursorB.close()
						


def dbdata(cnx2):
	
	c = cnx2.cursor()
	
	c.execute('''CREATE TABLE line_to_line_matches (
	source_line_id int,
	target_line_id int,
	co_citation_count int)''')

	c.execute('''CREATE TABLE lines (
	line VARCHAR(60),
	ftln int,
	play VARCHAR(50))''')
	
	c.execute('''CREATE TABLE docs (
	doi VARCHAR(50),
	title VARCHAR (200),
	journal VARCHAR (80),
	pubyear int,
	authors VARCHAR(200)
	)''')
	
	c.execute('''CREATE TABLE doc_to_matches_matches (
	lines_match_id int,
	doc_id int)''')
	



if __name__ == '__main__':
	play_act = options.p
	threshold = options.t
	
	build_play_lines_dictionary(play_act,threshold)
