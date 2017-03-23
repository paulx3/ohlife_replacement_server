import re
import sqlite3
import sys

def main():
  try:
    filename = sys.argv[1]
  except IndexError:
    print 'Usage: python import.py ohlife_export.txt'
    sys.exit(0)

  with sqlite3.connect('ohlife.db') as db:
    db.text_factory = str

    f = open(filename)
    day = ""
    entry = ""

    def write_to_db(day, entry):
      query = 'insert into entries (day, entry) values (?, ?)'
      db.execute(query, (day, entry))
      db.commit()
      print day, entry, '\n---------------------------------------------'

    for line in f.readlines():
      if re.match("(201[1-4]-[01][0-9]-[0-3][0-9])", line):
        if day and entry:
          write_to_db(day.strip("\r\n"), entry.strip("\r\n"))
        day = line
        entry = ""
      else:
        entry += line 

    write_to_db(day.strip("\r\n"), entry.strip("\r\n"))

    f.close()

if __name__ == '__main__':
    main()
