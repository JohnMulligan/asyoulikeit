# Shakespeare Passages Recommendation System

This repository holds the code for an intertextual recommendation system that links passages in the Shakespearean dramatic corpus (as digitized by Folger) to one another based entirely on scholarly citations/quotations (as identified by JSTOR Labs in their collection of digitized works, and made available in what was called their Matchmaker API). 

The web interface is currently running at https://theshakespearegame.rice.edu

The Critical Inquiry article is available at https://doi.org/10.1086/715982

The SQL database (and the code contained here) is available through the Rice digital scholarship archive https://doi.org/10.25611/kk2a-8888

## Application Folder

The web application uses

* MySQL back-end
* Python Flask to render pages and page elements
* jQuery to bind events to page elements

Prior versions of this application used SQLite databases in order to allow users to select between 1-20 line passages, but this greatly increases the amount of data that has to be handled. For smoother deployment, I've restricted the interface to 10-line passages. I am happy to provide the full set of sqlite databases upon request.

In order to deploy it you will need to create a database in a MySQL server using the .sql dump that is included in the Rice repository, and fill in the details of your connection in the config.py file I've provided.

Once that's done, you should be able to test it locally by setting up a virtual environment and kicking off the app:

	python3 -m venv venv
	source venv/bin/activate
	pip3 install -r requirements.txt
	python application.py
	
_it is worth noting that this interface could be improved upon. the flask templating, javascript handlers, styling, and database call layers are not completely abstracted from each other according to best practices. i am more than happy to include useful improvements by others in this codebase._

## Supercomputing Folder

This folder contains some samples of the supercomputing code I used to develop the recommendation database. What is not supplied is the original database from JSTOR's Matchmaker API, which I ran the code using. I am happy to supply that to people upon request, but because I have the qualitatively transformed database included in here, and the original dataset is (largely) a replication of part of JSTOR's data, it's not appropriate to reproduce it here, in my opinion.

I have included here a powerpoint that I used in a workshop which explains some of the processes involved. A longer, larger powerpoint presentation can be seen here: http://www.johncmulligan.net/blog/2019/10/14/2019-rice-data-science-conference/

The code is largely untouched and uncommented, and so references to files and variable names could, admittedly, be more reader-friendly.

### Lines Folder

These folders contain two experiments in finding the 29 million line-to-line co-citations implicit in the JSTOR/Folger dataset.

* The DAvinCI folder shows a typical experiment in which my different processes were coordinated and could communicate with each other via a message passing interface (MPI). These were run on Rice's since-retired DAvinCI cluster. MPI jobs are quite elegant but the coordination of processes can create a ceiling on performance.
* The HTCondor folder shows a typical experiment in which my processes operated independently, using the High-Throughput Computing (HPC) model of supercomputing. These were run on UW Madison's HTCondor network. These workflows require some pre-processing and planning, but they can scale linearly.

### Passages (Windows) Folder

This folder contains my experiment in using Rice's now-unified cluster, NOTS, to run an HTC job for precalculating all of the passages that a user might select. It is why the final database is a little larger but runs faster.