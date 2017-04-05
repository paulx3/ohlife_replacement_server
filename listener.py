import re
import sqlite3
from flask import request, Flask, render_template_string
import arrow
from bs4 import BeautifulSoup
app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string('home')


@app.route('/listen', methods=['POST'])
def listen():
    jsonGotten = request.get_json(force=True)
    print(jsonGotten)
    subject = jsonGotten["headers"]["Subject"]
    entry = BeautifulSoup(jsonGotten['html'])
    entry = entry.select('div[style]')[0].text
    day = today = arrow.now().format('YYYY-MM-DD')

    print(day)
    print(entry)
    print(subject)

    write_to_db(day, entry)

    return render_template_string('listen')


def write_to_db(day, entry):
    if day is not None and entry is not None:
        try:
            with sqlite3.connect('ohlife.db') as db:
                query = 'insert into entries (day, entry) values (?, ?)'
                db.execute(query, (day, entry))
                db.commit()
            print('successfully wrote to db')
        except:
            print('ERROR: failed to write to db')


if __name__ == '__main__':
    app.run('0.0.0.0', port=8000)
