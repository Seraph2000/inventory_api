from flask import g
import sqlite3
import os

dir_path = os.path.dirname(os.path.realpath('inventory.db'))

def connect_db():
    sql = sqlite3.connect(dir_path + '/inventory.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite3'):
        g.sqlite_db = connect_db()
    return g.sqlite_db