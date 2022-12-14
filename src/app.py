from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
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
    auth = request.headers.get('Authorization')


    if not auth:
        raise Exception('No auth provided')

    token = auth.split()[1]
    data = jwt.decode(token, app.config['SECRET_TOKEN'], ['HS256'])

    cur.execute("SELECT * FROM useraccount WHERE username = %s", (data['username'],))
    user = cur.fetchone()

    if cur.rowcount > 0:
        if user[2] != data['passhash']:
            raise Exception('Password incorrect. Please try again')
    else:
        raise Exception('User not found')

    return data


@app.route('/')
def Index():
    cur = mysql.connection.cursor()
    try:
        token_validation()
    except Exception as e:
        return e.args[0],401
    cur.execute('SELECT * FROM imdb_topgrossing')
    fetchdata = cur.fetchall()
    message =  'Hello, I am 18220086 Aldi Fadlian Sunan. Welcome to Top Movies Recommendation and Prediction!'
    cur.close()

    return jsonify(message, fetchdata)

@app.route('/read', methods=['GET'])
def read():
    cur = mysql.connection.cursor()
    try:
        token_validation()
    except Exception as e:
        return e.args[0],401
    movies_id = request.args.get('movies_id', type = int)
    title = request.args.get('title')
    certificate = request.args.get('certificate')
    distributor = request.args.get('distributor')
        
    cur.execute('SELECT * FROM imdb_topgrossing WHERE movies_id = %s OR title = %s OR certificate = %s OR distributor = %s', (movies_id, title, certificate, distributor))
    fetchdata = cur.fetchall()
    cur.close()

    return jsonify(fetchdata)

@app.route('/classification', methods=['GET'])
def classification():
    cur = mysql.connection.cursor()
    try:
        token_validation()
    except Exception as e:
        return e.args[0],401
    movies_id = request.args.get('movies_id', type = int)
    certificate = request.args.get('certificate')
    distributor = request.args.get('distributor')
        
    cur.execute("""
    SELECT distributor, COUNT(TITLE) AS "Jumlah Film", certificate, SUM(replace(gross, ',', '')) AS "Total Penghasilan", AVG(replace(gross, ',', '')) AS "Rata-rata Penghasilan" FROM imdb_topgrossing 
    WHERE (movies_id=%s OR certificate=%s OR distributor=%s)
    GROUP BY distributor, certificate
    ORDER BY distributor ASC, "Total Penghasilan" ASC
    """
    , (movies_id, certificate, distributor))
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

@app.route('/register')
def register():
    cur = mysql.connection.cursor()
    username = request.args.get('username')
    password = request.args.get('password')

    if not username or not password:
        return "Please fill the username and password below"

    passhash = generate_password_hash(password)

    cur.execute('SELECT * FROM useraccount WHERE username = %s', (username,))

    if cur.rowcount > 0:
        return "Username already exist"

    cur.execute("""
        INSERT INTO useraccount (
            username, passhash
            ) VALUES (
                %s, %s
            )
            """, (
                username,
                passhash
            ))
    mysql.connection.commit()
    return "Register successful, please login to get jwt token"

@app.route('/login')
def login():
    cur = mysql.connection.cursor()
    username = request.args.get('username')
    password = request.args.get('password')

    if not username or not password:
        return "Please provide username and password"

    cur.execute('SELECT * FROM useraccount WHERE username = %s', (username,))
    user = cur.fetchone()
    
    if cur.rowcount > 0:
        if check_password_hash(user[2], password):

            passhash = user[2]
            token = jwt.encode({
                'username': username,
                'passhash': passhash,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }, app.config['SECRET_TOKEN']
            )
            return token
        else:
            return "Incorrect password"
    else:
        return "User not found"

if __name__ == "__main__":
    app.run(debug = True)