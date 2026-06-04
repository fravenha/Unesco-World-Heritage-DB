-- Drop tables if they exist
DROP TABLE IF EXISTS Sites;
DROP TABLE IF EXISTS Risks;
DROP TABLE IF EXISTS Regions;
DROP TABLE IF EXISTS States;
DROP TABLE IF EXISTS Selections;
DROP TABLE IF EXISTS Dates;
DROP TABLE IF EXISTS Criterias;
DROP TABLE IF EXISTS Info_Risks;
DROP TABLE IF EXISTS Regions_Combinations;
DROP TABLE IF EXISTS Sites_Combinations;
DROP TABLE IF EXISTS All_Criterias;
DROP TABLE IF EXISTS Date_Combinations;



--Create tables for db
CREATE TABLE Sites (
    siteID INTEGER PRIMARY KEY,
    rev_bis VARCHAR(10),
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    danger INTEGER NOT NULL,
    longitude DOUBLE,
    latitude DOUBLE,
    area_hectares FLOAT,
    transboundary INTEGER NOT NULL
);

CREATE TABLE Risks (
    riskID INTEGER PRIMARY KEY AUTOINCREMENT,
    type CHAR(1) NOT NULL,
    date_end INTEGER,
    year INTEGER,
    period_Start INTEGER,
    period_End INTEGER
);

CREATE TABLE Info_Risks (
    riskID INTEGER NOT NULL,
    siteID INTEGER NOT NULL,     
    FOREIGN KEY (riskID) REFERENCES Risks(riskID)
    FOREIGN KEY(siteID) REFERENCES Sites(siteID)
);

CREATE TABLE Regions (
    regionID INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE
);

CREATE TABLE States (
    stateID INTEGER PRIMARY KEY AUTOINCREMENT,
    regionID INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    iso_code VARCHAR(2) UNIQUE,
    udnp_code VARCHAR(3) UNIQUE,
    FOREIGN KEY (regionID) REFERENCES Regions(regionID)
);

CREATE TABLE Sites_Combinations (
    siteID INTEGER NOT NULL, 
    stateID INTEGER NOT NULL,
    FOREIGN KEY (siteID) REFERENCES Sites(siteID),
    FOREIGN KEY (stateID) REFERENCES States(stateID)
);

CREATE TABLE Selections (
    selectionID INTEGER PRIMARY KEY,
    siteID INTEGER NOT NULL UNIQUE,
    justification TEXT,
    year_inscribed INTEGER NOT NULL,
    category_short VARCHAR(3) NOT NULL,
    category VARCHAR(8) NOT NULL,
    criteria_txt VARCHAR(28) NOT NULL,
    FOREIGN KEY (siteID) REFERENCES Sites(siteID)
);

CREATE TABLE Criterias (
    sigla CHAR(2) PRIMARY KEY,
    description VARCHAR(280) NOT NULL
);

CREATE TABLE All_Criterias (
    selectionID INTEGER NOT NULL, 
    sigla CHAR(2) NOT NULL, 
    FOREIGN KEY (selectionID) REFERENCES Selections(selectionID),
    FOREIGN KEY (sigla) REFERENCES Criterias(sigla)
);

CREATE TABLE Dates (
    dateID INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL UNIQUE
);

CREATE TABLE Date_Combinations (
    selectionID INTEGER NOT NULL,
    dateID INTEGER NOT NULL, 
    FOREIGN KEY (selectionID) REFERENCES Selections(selectionID),
    FOREIGN KEY (dateID) REFERENCES Dates(dateID)
);