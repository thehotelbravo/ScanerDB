import nmap
import sys
import sqlite3
import csv

nm = nmap.PortScanner()
input_args = raw_input(""" Please make your selection of the different scan options:
                            1: Full aggresive scan
                            2: Basic port/service scan
                            3: Stealthy silent scan
                            """)
hostlist = sys.argv[1]
conn = sqlite3.connect('../../scan.db')
c = conn.cursor()

def scanner():
    if input_args == "1":
        args = "-T4 -A -v"
    elif input_args == "2":
        args = "-sV"
    elif input_args == "3":
        args = "-sS"
    else:
        print "No viable options selected. Please either type 1, 2 or 3"
    nm.scan(hosts= hostlist, arguments= args)
    csvfile = open('/tmp/results.csv', 'w+')
    csvfile.write(nm.csv())
    
#scans hosts and places results into csvfile

def sqlimport():
    c.execute("drop table if exists Stageing")
    c.executescript("""
       Create table Stageing
       (host INTEGAR,
       hostname VARCHAR,
       port INTEGAR,
       name VARCHAR,
       state VARCHAR, 
       product VARCHAR,
       version VARCHAR
       );
       """)
    c.executescript("""
       Create table IF NOT EXISTS Results
       (host INTEGAR,
       hostname VARCHAR,
       port INTEGAR,
       name VARCHAR,
       state VARCHAR,
       product VARCHAR,
       version VARCHAR
       );
       """)
    reader = csv.reader(open('/tmp/results.csv', 'r'), delimiter=';')
    for row in reader:
        to_db = [unicode(row[0], "utf8"), unicode(row[1], "utf8"), unicode(row[4], "utf8"), unicode(row[5], "utf8"), unicode(row[6], "utf8"), unicode(row[7], "utf8"), unicode(row[10], "utf8")]
        c.execute("INSERT INTO Stageing (host, hostname, port, name, state, product, version) VALUES (?, ?, ?, ?, ?, ?, ?);", to_db)
        c.execute("insert into results select * from stageing as a where not exists (select 'x' from results as b where a.host = b.host and a.hostname = b.hostname and a.port = b.port)")
    #c.execute("INSERT INTO Results ( SELECT * FROM Stageing A WHERE NOT EXISTS(SELECT * FROM Results B WHERE A.host = B.host);")
    #c.execute("INSERT INTO Results ( SELECT * FROM Stageing A WHERE NOT EXISTS(SELECT * FROM Results B WHERE A.hostname = B.hostname);")
    #c.execute("INSERT INTO Results ( SELECT * FROM Stageing A WHERE NOT EXISTS(SELECT * FROM Results B WHERE A.port = B.port);")
    #c.execute("INSERT INTO Results ( SELECT * FROM Stageing A WHERE NOT EXISTS(SELECT * FROM Results B WHERE A.name = B.name);")
    #c.execute("INSERT INTO Results ( SELECT * FROM Stageing A WHERE NOT EXISTS(SELECT * FROM Results B WHERE A.state = B.state);")
    #c.execute("INSERT INTO Results ( SELECT * FROM Stageing A WHERE NOT EXISTS(SELECT * FROM Results B WHERE A.product = B.product);")
    #c.execute("INSERT INTO Results ( SELECT * FROM Stageing A WHERE NOT EXISTS(SELECT * FROM Results B WHERE A.version = B.version);")
    conn.commit()
#Imports the results.csv file into a stageing table.

scanner()
sqlimport() 
