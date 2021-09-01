from flask import Flask, request, render_template, redirect
import re
import json
import os
import mysql.connector
import time
from config import *


application = app = Flask(__name__)

def format_title(title):
	formatted_title = re.sub("_"," ",title)
	formatted_title = re.sub("\.",": ",formatted_title,1)
	formatted_title = formatted_title.title()
	roman_numerals = re.compile("( Vi+| Iv| I[i]+)")
	try:
		rn = re.search(roman_numerals,formatted_title).group(0)
		formatted_title = re.sub(rn,rn.upper(),formatted_title)
	except:
		pass
	return formatted_title

def get_random_play():
	cnx = mysql.connector.connect(**conf)
	cursor = cnx.cursor()
	query="select distinct play from play_boundary order by rand() limit 1;"
	cursor.execute(query)
	play=cursor.fetchone()[0]
	cnx.close()
	return(play)

def get_play_boundaries(play):
	cnx = mysql.connector.connect(**conf)
	cursor = cnx.cursor()
	query="select startline_id,endline_id from play_boundary where play='%s'" %play
	cursor.execute(query)
	play_boundaries=cursor.fetchone()
	cnx.close()
	return play_boundaries

def get_window_rowids(rowid,n):
	rowid=int(rowid)
	n=int(n)
	play,ftln,play_line=get_rowid_info(rowid)
	play_min_rowid,play_max_rowid=get_play_boundaries(play)
	print(play_min_rowid,play_max_rowid)
	if rowid+n>play_max_rowid:
		startline_rowid=play_max_rowid-n
	else:
		startline_rowid=rowid
	endline_rowid=startline_rowid+n
	print(startline_rowid,endline_rowid)
	return [i for i in range(startline_rowid,endline_rowid+1)]

def get_rowid_info(rowid):
	cnx = mysql.connector.connect(**conf)
	cursor = cnx.cursor()
	query="SELECT play,ftln,line from play_lines where rowid=%s"
	cursor.execute(query,[(rowid)])
	play,ftln,play_line = cursor.fetchone()
	cnx.close()
	return play,ftln,play_line

def get_passage(rowid,n=10,maintext=True):
	cnx = mysql.connector.connect(**conf)
	cursor = cnx.cursor()
	play,ftln,play_line=get_rowid_info(rowid)
	if maintext==True:
		#then fetch all
		play_startline_rowid,play_endline_rowid=get_play_boundaries(play)
		n=play_endline_rowid-play_startline_rowid	
	query="SELECT rowid,ftln,line_text,play,line FROM play_lines WHERE rowid >= %s AND rowid < %s order by ftln asc"
	data=[(int(rowid),int(rowid)+n)]
	if maintext==True:
	    print(query,data)
	cursor.execute(query,data[0])
	passage_text=cursor.fetchall()
	pretty_line_html = ''
	if len(passage_text)!=0:
		start_rowid,start_ftln,start_line_text,play,start_play_line =passage_text[0]
		for line in passage_text:
			rowid,ftln,line_text,play,play_line = line
			if maintext==False:
				rowid=start_rowid
			line_set = line_text.split('\n')
			for subline in line_set:
				clean_sub = subline.strip()
				if maintext==True:
					if re.match("([A-Z]{2,}.*)|((Enter|Exit) [A-Z].*)|(Scene [1-9].*)|([A-Z][^ ]+ (exits|enters).*)",clean_sub,re.S):
						pretty_line_html += '<br/>%s<br/>' %(clean_sub)
					elif clean_sub == '':
						pass
					else:
						pretty_line_html += '<br/><a id="%s" class="T">%s</a><br/>' %(str(rowid),clean_sub)
				else:
					if clean_sub == '':
						pass
					else:
						pretty_line_html += '<a id="%s-%s" class="C">%s</a><br/>' %(str(n),str(rowid),clean_sub)
	else:
		start_ftln=rowid
		pretty_line_html="<center>No correlated texts (unusual!)</center>"
	cnx.close()
	return pretty_line_html,play,start_play_line,start_ftln
	
def get_articles(source,target,n):
	cnx = mysql.connector.connect(**conf)
	cursor = cnx.cursor()
	match_table = 'docs_%d' %n
	query="select docs from %s where source_id = %d and target_id = %d" %(match_table,source,target)
	cursor.execute(query)
	doc_rowids=cursor.fetchone()
	html_block = ''
	if doc_rowids!=None:
		#doc_rowids=[int(i) for i in doc_rowids[0].split(',')]
		query="select doi,title,journal,pubyear,authors from articles where rowid in (%s) order by pubyear asc;" %str(doc_rowids[0])
		cursor.execute(query)
		docs=cursor.fetchall()
		for doc in docs:
			doi,title,journal,pubyear,authors=doc
			template = "<p><a class=\"articlelink\" href='http://jstor.org/stable/%s' target='_blank'>%s</a><br/><span class=\"articletext\" By: %s<br/>%s: %s<br/></span></p><hr/>" %(doi,title,authors,pubyear,journal)
			html_block += template	
	cnx.close()
	return html_block
		
def get_play_boundaries(play):
	cnx = mysql.connector.connect(**conf)
	cursor = cnx.cursor()
	query="select startline_id,endline_id from play_boundary where play='%s'" %play
	play_boundaries = cursor.execute(query)
	play_boundaries=cursor.fetchone()
	cnx.close()
	return play_boundaries

def get_gamestate_link(rowid,n=10):
	gamestate_link=render_template('gamestate_link.html', n=n,rowid=rowid)
	return(gamestate_link)

def ariel(passage_start_rowid,n=10,k=10):
	cnx = mysql.connector.connect(**conf)
	cursor = cnx.cursor()
	match_table = 'matches_%d' %n
	match_passages=[]
	passage_start_rowid=min(get_window_rowids(passage_start_rowid,n))
	searchstring = "SELECT * FROM " + match_table + " WHERE source_id = %s"
	data=[(passage_start_rowid)]
	cursor.execute(searchstring,data)
	matches=cursor.fetchone()
	
	for c in range(k+1):
		match_passage_first_line_rowid=matches[2*c+2]
		match_passage_score=matches[2*c+3]
		if match_passage_first_line_rowid!=None:
			match_article_html = "<a id=\"%s-%s\" class=\"A\">~View co-citing articles (score of %s)~</a>" %(str(passage_start_rowid),str(match_passage_first_line_rowid),str(match_passage_score))
			match_passage_html,this_play,line,start_ftln = get_passage(match_passage_first_line_rowid,n,maintext=False)
			disp_line = format_title(line)
			match_passages.append({
				"play":this_play,
				"ftln":start_ftln,
				"line":line,
				"disp_line":disp_line,
				"rowid":match_passage_first_line_rowid,
				"match_article_html":match_article_html,
				"match_passage_html":match_passage_html
				})
	match_html_block=render_template('infratexts.html',match_passages=match_passages)
	cnx.close()
	return match_html_block

@app.route("/")
def miranda():
	n=10
	k=10
	pd = {a:request.args[a] for a in request.args}
	passage_start_rowid=None
	infratext_html_block=''
	selected_rowids=None
	if 'play' not in pd and 'rowid' not in pd:
		#then we're just landing without having selected anything
		play=get_random_play()
		rowid=None
	elif 'play' in pd and 'rowid' not in pd:
		#then we have a play selected but not a passage
		play=pd['play']
		rowid=None
	elif 'rowid' in pd:
		#then we have a selected play passage
		rowid=int(pd['rowid'])
		play,ftln,line=get_rowid_info(rowid)
		infratext_html_block=ariel(rowid,n,k)
	formatted_title=format_title(play).upper()
	play_startline_rowid,play_endline_rowid=get_play_boundaries(play)
	#guarantee a passage of n lines is selected (if any line is selected)
	if rowid!=None:
		if rowid+n>play_endline_rowid-1:
			rowid=play_endline_rowid-n
		selected_rowids=[i for i in range(rowid,n+1)]
	play_html_block,play,play_line,start_ftln=get_passage(play_startline_rowid,maintext=True)
	gamestate_link=get_gamestate_link(rowid,n)
	return render_template("as_you_like_it.html",
		play=formatted_title,
		play_html_block=play_html_block,
		rowid=rowid,
		n=n,
		selected_rowids=selected_rowids,
		infratext_html_block=infratext_html_block,
		gamestate_link=gamestate_link
	)
    
@app.route('/correlated_texts/<rowid>/<n>')
def correlated_texts(rowid,n):
	infratexts_html_block=ariel(rowid,n=10,k=10)
	if infratexts_html_block=='':
		infratexts_html_block="<p>no matches.</p>"
	return infratexts_html_block

@app.route('/get_articles/<source>/<target>/<n>')
def articles(source,target,n):
	articles_html_block= get_articles(int(source),int(target),int(n))
	return articles_html_block

@app.route('/get_gamestate_link/<rowid>/<n>')
def gamestate_link(rowid,n):
	gamestate_html_block= get_gamestate_link(rowid,n)
	return gamestate_html_block
	


@app.route('/get_selection/<rowid>/<n>')
def get_selection(rowid,n):
	selection=get_window_rowids(rowid,n)
	return json.dumps({"s":selection})

if __name__ == "__main__":
	application.run()

