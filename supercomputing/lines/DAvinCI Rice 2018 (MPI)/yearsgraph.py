import sqlite3

def main():
		jstor_shakespeare_db = sqlite3.connect('shakespeare_clean.db')
		jstor_shakespeare_cursor = jstor_shakespeare_db.cursor()
		minyear,maxyear = jstor_shakespeare_cursor.execute("select min(pubyear),max(pubyear) from articles;").fetchone()
		d = open("out.csv","a")
		for year in range(minyear,maxyear+1):
			query = "select count(*) from articles where pubyear = %d;" %year
			articlecount=jstor_shakespeare_cursor.execute(query).fetchone()
			
			if articlecount != []:
				outstring = "%d,%d\n" %(year,articlecount[0])
				d.write(outstring)
		d.close()
		
if __name__ == '__main__':
	main()