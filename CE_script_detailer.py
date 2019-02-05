#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
C:E Scripts report generator
"""

import sqlite3

def script_info_extractor(report_file_path):
   
    try:
        fp = open(report_file_path, 'r')
        
    except Exception as e:
        return e
        
    report_content = fp.read().split('\n')
    scripts_detail = {}
    report_file_entry = 0
    
    for script_report in report_content:
        
        report_file_entry = report_file_entry + 1
        script_info = script_report.split(' ')
        if len(script_info) != 3:
            print(">> Ignoring entry (fewer details): info count=%d, entry no. %d\n" \
                  % (len(script_info), report_file_entry))
            continue
        
        script_name = script_info[0]
        month = script_info[1]
        count = script_info[2]
        
        #Update script info
        if script_name in scripts_detail.keys():
            scripts_detail[script_name].append((month, count))
        else:
            #Coming across this script the first time, create an entry
            scripts_detail[script_name] = [(month, count)]
   
    fp.close()
    return scripts_detail

       

'''In-memory db'''
def build_scripts_db():

    month_info = [
        (1,'Jan'), (2,'Feb'), (3,'Mar'), (4,'Apr'),
        (5,'May'), (6,'Jun'), (7, 'Jul'), (8,'Aug'), (9,'Sep'),
        (10,'Oct'), (11,'Nov'), (12,'Dec')]

    #Create a database to store script details
    db_conn = sqlite3.connect(":memory:")
    db_conn.executescript('''
        DROP TABLE IF EXISTS scripts;
        DROP TABLE IF EXISTS months;
    
        CREATE TABLE scripts
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL);
  
        CREATE TABLE months
            (id INTEGER PRIMARY KEY,
              month TEXT NOT NULL);
        
        CREATE TABLE scripts_run_info
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            script_name TEXT  
                 CONSTRAINT fks NOT NULL REFERENCES scripts(name),
             month TEXT
                 CONSTRAINT fkm NOT NULL REFERENCES months(month),
            runs INTEGER NOT NULL);
        ''')
            
    #insert months data
    db_conn.executemany("INSERT INTO months (id, month) values(?,?)", month_info)
    
    return db_conn



'''Load scripts information into in:memory database'''
def load_scripts_info_to_db(scripts_detail):
    
    '''create an in:memory db'''
    dbc = build_scripts_db()
    for script_name, run_info in zip(scripts_detail.keys(), scripts_detail.values()):
        dbc.execute("INSERT INTO scripts (name) values(?)", [(script_name)])
        for m in run_info:
            month = m[0]
            run = int( m[1])
            dbc.execute('''
                INSERT INTO scripts_run_info (script_name, month, runs)
                VALUES(?,?,?)''', [(script_name, month, run)])
            
    result = dbc.execute('''SELECT * FROM scripts_run_info''')
    print("Database content\n%s" % result.fetchall())
    
    return
    

'''Load scripts info in scripts db'''
def print_scripts_detail(scripts_detail):
    
    if type(scripts_detail) != dict:
        print("Scripts detail provided is not a disctionary type")
        return False
           
    total_runs = 0
    for script_name, run_info in zip(scripts_detail.keys(), scripts_detail.values()):
        print("Script: %s" % script_name)
        for m in run_info:
            print("   %s = %d" % (m[0], int(m[1])))
            total_runs = total_runs + int(m[1])
        print("   Total runs = %d" % total_runs)
    return


'''Main program'''
def main():
    
    #path1 = input("Please provide the pathname for the scripts report file:")
    path1 = 'report1.txt'
    details = script_info_extractor(path1)
    
    if type(details) == dict:
        #print_scripts_detail(details)
        #print("\nIn JSON format: \n\n%s" % details)
        load_scripts_info_to_db(details)
        
    else:
        print("Some error happened:\n%s" % details)
    
    
    return


'''Call main program'''
if __name__ == '__main__':
    main()
    
