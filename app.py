import requests
from flask import Flask
from database import cursor,db
from flask import request, jsonify
from flask import redirect, abort
import hashlib
from urllib.parse import urlparse

import re

app = Flask(__name__)

#create
@app.route('/', methods=['POST'])
def create_shortening_url():
    data = request.get_json()
    #processing the data submitted in the request and returns an error code 400 if the data is not legal.
    if not data or 'full_url' not in data:
        abort(400)

    full_url = data['full_url']

    #validate the url format
    if not is_valid_url(full_url):
        abort(400, 'Wrong Format URL')

    #validate if the url is exist
    if not is_exist_url(full_url):
        abort(400, 'URL Does Not Exist')
    # use md5(hash function) for the shortening URL
    m = hashlib.md5()
    m.update(data['full_url'].encode('utf-8'))
    shortening_url = m.hexdigest()[:8]

    # insert the shortening url and the full url (mapping)to the database(mysql)
    cursor.execute("INSERT INTO urls (shortening_url, full_url) VALUES (%s, %s)", (shortening_url, data['full_url']))
    db.commit()
    # Returns the generated shortening link and converts the dictionary into a JSON formatted response using the jsonify function provided by Flask.
    return jsonify({'shortening_url': shortening_url})

#GET request（default）
@app.route('/<string:id>')
def redirect_to_url(id):
    # get the value of the only element of this tuple, which is the full_url
    cursor.execute("SELECT full_url FROM urls WHERE shortening_url=%s", (id,))

    url = cursor.fetchone()
    # if the 'select' failed, abort error 404
    if url is None:
        abort(404)
    else:
        #redirect to the full_url page
        return redirect(url[0], code=301)

#change the
@app.route('/<string:id>', methods=['PUT'])
def update_url(id):
    data = request.get_json()
     #processing the data submitted in the request and returns an error code 400 if the data is not legal.
    if not data or 'full_url' not in data:
        abort(400)
    #The full_url corresponding to the given shortening_url id is updated to the full_url value provided in the request.
    full_url = data['full_url']

    #validate the url format
    if not is_valid_url(full_url):
        abort(400, 'Wrong Format URL')

    #validate if the url is exist
    if not is_exist_url(full_url):
        abort(400, 'URL Does Not Exist')

    cursor.execute("UPDATE urls SET full_url=%s WHERE shortening_url=%s", (data['full_url'], id))

    #commit the changes to the database.
    db.commit()
    #Check if the UPDATE operation was successful. If no rows were updated, then the given shortening_url id does not exist in the database and an HTTP 404 error is returned. Otherwise, a JSON response is returned with a success message.
    if cursor.rowcount == 0:
        abort(404)
    else:
        return jsonify({'message': 'URL updated successfully'})

@app.route('/<string:id>', methods=['DELETE'])
def delete_url(id):
    cursor.execute("DELETE FROM urls WHERE shortening_url=%s", (id,))
    db.commit()

    #Check if the delete operation was successful. If no rows were delete, then the given shortening_url id does not exist in the database and an HTTP 404 error is returned. Otherwise, a JSON response is returned with a success message.
    if cursor.rowcount == 0:
        abort(404)
    else:
        return jsonify({'message': 'URL deleted successfully'})

@app.route('/all', methods=['DELETE'])
def delete_all_url():
    cursor.execute("DELETE FROM urls")
    db.commit()

    #Check if the delete operation was successful. If no rows were delete, then the given shortening_url id does not exist in the database and an HTTP 404 error is returned. Otherwise, a JSON response is returned with a success message.
    if cursor.rowcount == 0:
        abort(404)
    else:
        return jsonify({'message': 'All URL deleted successfully'})
#GET request
@app.route('/')
def get_all_urls():
    cursor.execute("SELECT shortening_url FROM urls")

    #show all
    urls = cursor.fetchall()

    return jsonify({'urls': [url[0] for url in urls]})


#validate the format of url
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

#validate the existence of url
def is_exist_url(url):
    try:
        response = requests.get(url)
        # return response.status_code < 400
        return True
    except requests.exceptions.RequestException:
        return False

if __name__ == '__main__':
    app.run(debug=True)