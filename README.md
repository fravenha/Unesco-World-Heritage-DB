# UNESCO World Heritage Information System

A Flask-based web application for exploring and analyzing UNESCO World Heritage Sites through an interactive SQLite database.

## Overview

This project was developed as a database-driven information system focused on UNESCO World Heritage Sites. The application allows users to browse sites, regions, countries, criteria, risks, and selections, while also providing a set of analytical queries over the stored data.

The system uses a relational database populated from UNESCO data and offers a web interface for easy exploration of the information.

## Features

* Browse all UNESCO World Heritage Sites
* View detailed information about individual sites
* Explore regions and participating countries
* Access UNESCO selection criteria
* View risk classifications
* Navigate through selection records
* Execute analytical database queries
* Interactive web interface built with Flask
* SQLite database integration

## Technologies Used

* Python 3
* Flask
* SQLite
* HTML
* Jinja2 Templates

## Project Structure

```text
final_project/
│
├── app.py                     # Main Flask application
├── server.py                  # Server startup script
├── db.py                      # Database connection utilities
├── world_heritage.db          # SQLite database
├── test_db_connection.py      # Database connection tests
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── site.html
│   ├── site-list.html
│   ├── region.html
│   ├── region-list.html
│   ├── state.html
│   ├── state-list.html
│   ├── criteria-list.html
│   ├── risk-list.html
│   ├── selection-list.html
│   ├── question1.html
│   ├── question2.html
│   ├── question3.html
│   ├── question4.html
│   ├── question5.html
│   ├── question6.html
│   ├── question7.html
│   ├── question8.html
│   ├── question9.html
│   └── question10.html
│
└── Povoamento/
    ├── save_info.py           # Data population script
    ├── tabelas.sql            # Database schema
    ├── whc-sites-2024.xls     # UNESCO source dataset
    └── README.md
```

## Database

The application uses a SQLite database containing information about:

* World Heritage Sites
* Regions
* States Parties
* UNESCO Criteria
* Risk Categories
* Selection Records

The database is populated from UNESCO's World Heritage dataset.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository
```

### 2. Create a virtual environment (optional)

```bash
python -m venv venv
```

Activate the environment:

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install flask
```

## Running the Application

Start the server with:

```bash
python server.py
```

The application will be available at:

```text
http://localhost:9001
```

## Available Pages

### Main Navigation

* Home Page
* Sites
* Regions
* States
* Criteria
* Risks
* Selections

### Analytical Queries

The system includes several predefined analytical queries available through dedicated routes:

* Question 1
* Question 2
* Question 3
* Question 4
* Question 5
* Question 6
* Question 7
* Question 8
* Question 9
* Question 10

These queries demonstrate the use of SQL for data analysis and information retrieval.

## Data Population

The `Povoamento` folder contains the scripts and resources used to populate the database from UNESCO's dataset.

To generate or update the database:

1. Use the UNESCO source file (`whc-sites-2024.xls`)
2. Execute the population script
3. The information is automatically inserted into the SQLite database

## Learning Objectives

This project demonstrates:

* Relational database design
* SQL querying
* Data extraction and transformation
* Backend web development with Flask
* Database integration with Python
* Dynamic web page generation using templates

## Authors

* Flávia Queiroz
* Sara Soares

## License

This project was developed for academic purposes.
