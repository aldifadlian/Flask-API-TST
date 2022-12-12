from flask import Flask, request, jsonify
import secrets
from flask_mysqldb import MySQL
import datetime
import jwt

app = Flask(__name__)
app.config['SECRET_TOKEN'] = 'J9YPPNlJ1V4SeM_lxsiA8g'

app.config['MySQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'alliswell82'
app.config['MYSQL_DB'] = 'tst'

mysql = MySQL(app)

def token_validation():
    cur = mysql.connection.cursor()
    api_key = request.headers.get('api-key')

    if not api_key:
        raise Exception('No auth provided')

    cur.execute('SELECT * FROM userapikeys WHERE api_key = %s', (api_key,))
  
    if cur.rowcount < 1:
        raise Exception('Invalid api key')

    return api_key

@app.route('/generate_api_key')
def generate_api_key():
    cur = mysql.connection.cursor()
    api_key = secrets.token_urlsafe(64)
    cur.execute('INSERT INTO userapikeys (api_key) VALUES (%s)', (api_key,))
    mysql.connection.commit()
    return api_key

@app.route('/')
def Index():
    cur = mysql.connection.cursor()
    try:
        token_validation()
    except Exception as e:
        return e.args[0],401
    cur.execute('SELECT * FROM imdb_topgrossing')
    fetchdata = cur.fetchall()
    cur.close()

    return jsonify(fetchdata)

@app.route('/read', methods=['GET'])
def read():
    cur = mysql.connection.cursor()
    try:
        token_validation()
    except Exception as e:
        return e.args[0],401
    movies_id = request.args.get('movies_id', type = int)
    title = request.args.get('title')
        
    cur.execute('SELECT * FROM imdb_topgrossing WHERE movies_id = %s OR title = %s', (movies_id, title))
    fetchdata = cur.fetchall()
    cur.close()

    return jsonify(fetchdata)

@app.route('/insert', methods=['POST'])
def insert():

        cur = mysql.connection.cursor()

        try:
            token_validation()
        except Exception as e:
            return e.args[0],401

        cur.execute("""
        INSERT INTO imdb_topgrossing (
            Title, Movie_Info, Distributor, Release_date, Domestic_Sales_in_, International_Sales_in_, World_Sales_in_, Genre, Certificate, Runtime, IMDB_Rating, Meta_score, Director, Gross
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """, (
                request.args.get('Title'),
                request.args.get('Movie_Info'),
                request.args.get('Distributor'),
                request.args.get('Release_Date'),
                request.args.get('Domestic_Sales_in_', type=int),
                request.args.get('International_Sales_in_', type=int),
                request.args.get('World_Sales_in_', type=int),
                str(request.args.getlist('Genre')),
                request.args.get('Certificate'),
                request.args.get('Runtime'),
                request.args.get('IMDB_Rating', type=float),
                request.args.get('Meta_score'),
                request.args.get('Director'),
                request.args.get('Gross')
            ))
        mysql.connection.commit()
        return "Data berhasil ditambahkan"


@app.route('/update',methods=['PUT'])
def update():
        cur = mysql.connection.cursor()

        try:
            token_validation()
        except Exception as e:
            return e.args[0],401

        movies_id = request.args.get('movies_id', type = int)
        
        cur.execute('SELECT * FROM imdb_topgrossing WHERE movies_id = %s', (movies_id,))
        now = cur.fetchone()

        cur.execute("""
        UPDATE imdb_topgrossing 
        SET
            Title = %s,
            Movie_Info = %s, 
            Distributor = %s, 
            Release_Date = %s, 
            Domestic_Sales_in_ = %s,
            International_Sales_in_ = %s, 
            World_Sales_in_ = %s, 
            Genre = %s,
            Certificate = %s, 
            Runtime = %s, 
            IMDB_Rating = %s, 
            Meta_score = %s, 
            Director = %s, 
            Gross = %s
        WHERE movies_id = %s
        """, (
            request.args.get('Title', now[0]),
            request.args.get('Movie_Info', now[1]),
            request.args.get('Distributor', now[2]),
            request.args.get('Release_Date', now[3]),
            request.args.get('Domestic_Sales_in_', now[4], int),
            request.args.get('International_Sales_in_', now[5], int),
            request.args.get('World_Sales_in_', now[6], int), 
            str(request.args.getlist('Genre')) if request.args.getlist('Genre') else now[7],
            request.args.get('Certificate', now[8]), 
            request.args.get('Runtime', now[9]), 
            request.args.get('IMDB_Rating', now[10], float),
            request.args.get('Meta_score', now[11]),
            request.args.get('Director', now[12]), 
            request.args.get('Gross', now[13]),
            movies_id
            ))
        mysql.connection.commit()
        return "Data berhasil diupdate"


@app.route('/delete', methods = ['DELETE'])
def delete():
    cur = mysql.connection.cursor()
    try:
        token_validation()
    except Exception as e:
        return e.args[0],401

    movies_id = request.args.get('movies_id', type=int)
    cur.execute('DELETE FROM imdb_topgrossing WHERE movies_id = %s', (movies_id,))
    mysql.connection.commit()
    return "Data berhasil dihapus"

if __name__ == "__main__":
    app.run(debug = True)