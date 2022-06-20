# SimilarRepoBackend
This repository represents the backend for the application Hierarchy Visualiser: [Deployed app](https://hierarchy-visualiser.herokuapp.com/) developed by Andrei Ionescu during his Research Project CSE3000 (Bachelor Thesis) at the Delft University of Technology.

## Background
Developers do not want to reinvent the wheel when establishing a new software system. Open-source software
repositories are packed with resources that may assist developers with their work. Our research intends to
assist developers in locating such resources, allowing them to concentrate on the essential functions of an
application or system rather than implementing fundamental functionalities from scratch.
Each repository tag englobes knowledge about the application that is developed in a particular repository,
and a set of tags represents the architecture, and the overall system characteristics and dependencies.
Since GitHub enabled the repository tagging, a new opportunity arose to help the developers to find the
needed resources based on their needs.

The currently available literature and tools do not offer many solutions directly related to recommending
similar repositories which are tailored and based on the researcher or developer’s needs. Recommender
systems and tools can identify comparable repositories, but they focus on static approaches that can be
used just for a small number of repositories (e.g. Java Repositories). Furthermore, some of these approaches
are limited to their training data and cannot adapt to newly published repositories or technologies.
During our research, we aim to address the recommendation generality gap in recommending similar
repositories. 

## Initial Setup
Run: `pip install -r requirements.txt`

Add your Google Programmable Search API KEY in `./util/google.py`

Add your database connection URL in `./database.py`

## Feedback Database Setup
The database should contain a table named `feedback` with the following structure:
| Column Name 	| Type 	|
|:---:	|:---:	|
| id 	| int 	|
| githubLinks 	| JSON 	|
| ownLinks 	| JSON 	|
| githubPreferences 	| JSON 	|
| ownPreferences 	| JSON 	|
| extraInfo 	| JSON 	|

## How to run:
`uvicorn main:app --reload` or run `python main.py`

## Info
The application will lauch by default on the port `8000` and can be accessed using `localhost:800`
