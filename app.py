from flask import Flask, request, jsonify, send_file, send_from_directory
from requests.exceptions import HTTPError
import onesignal as onesignal_sdk
from flask_sqlalchemy import SQLAlchemy
from operator import itemgetter
from flask_marshmallow import Marshmallow
from marshmallow import fields
from flask_uploads import UploadSet, configure_uploads, IMAGES
import requests
import sys
import json
import urllib, http.client, base64, json
import time
import os
import os.path
import uuid
import datetime
import time
import pytz
local_tz = pytz.timezone('Canada/Torento')

isRecognizing = False
		


BaseDirectory = '/home/photos/detected/'
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
ma = Marshmallow(app)
url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0'
KEY = '0f8d012f2f5e4a04b7af47ae077ab9c7'
group_id = 'users'
fileList = [] # list of filePaths that were passed through as images
faceIdList = [] # list for face id's generated using api - detect
confidenceList = [] # list of confidence values derived from api - identif
directory = ""

def iter():
    for fileName in os.listdir(directory):
        if fileName.endswith('.jpg'):
            filePath = os.path.join(directory, fileName) # joins directory path with filename to create file's full path
            fileList.append(filePath)
            detect(filePath)

# detects faces in images from previously stated directory using azure post request
def detect(img_url):
    headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': KEY}
    body = open(img_url,'rb')

    params = urllib.urlencode({'returnFaceId': 'true'})
    conn = http.client.HTTPSConnection('westcentralus.api.cognitive.microsoft.com')
    conn.request("POST", '/face/v1.0/detect?%s' % params, body, headers)
    response = conn.getresponse()
    photo_data = json.loads(response.read())

    if not photo_data: # if post is empty (meaning no face found)
        print('No face identified')
    else: # if face is found
        for face in photo_data: # for the faces identified in each photo
            faceIdList.append(str(face['faceId'])) # get faceId for use in identify

# Takes in list of faceIds and uses azure post request to match face to known faces
def identify(ids):
    if not faceIdList: # if list is empty, no faces found in photos
        result = [('n', .0), 'n'] # create result with 0 confidence
        return result # return result for use in main
    else: # else there is potential for a match
        headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': KEY}
        params = urllib.urlencode({'personGroupId': group_id})
        body = "{'personGroupId':'"+group_id+"', 'faceIds':"+str(ids)+", 'confidenceThreshold': '.5'}"
        conn = http.client.HTTPSConnection('westcentralus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/identify?%s" % params, body, headers)
        response = conn.getresponse()

        data = json.loads(response.read()) # turns response into index-able dictionary
        print(data)
        for resp in data:
            candidates = resp['candidates']
            for candidate in candidates: # for each candidate in the response
                confidence = candidate['confidence'] # retrieve confidence
                personId = str(candidate['personId']) # and personId
                confidenceList.append((personId, confidence))
        conn.close()
        SortedconfidenceList = zip(confidenceList, fileList) # merge fileList and confidence list
        sortedConfidence = sorted(SortedconfidenceList, key=itemgetter(1)) # sort confidence list by confidence
        return sortedConfidence[-1] # returns tuple with highest confidence value (sorted from smallest to biggest)


# takes in person_id and retrieves known person's name with azure GET request
def getName(person_Id):
    user = db.session.query(User).filter(User.azure_id==person_Id).first()
    return user


def facial_recognition():
    camera = PiCamera() # initiate camera
    count = 0
    while True:
        count+=1
        directory = BaseDirectory+str(uuid.uuid4().hex)+'/'
        os.mkdir(directory) # make new directory for photos to be uploaded to
        print(count)
        print(directory)
        for x in range(0,3):
            date = datetime.datetime.now().strftime('%m_%d_%Y_%M_%S_') # change file name for every photo
            camera.capture(directory + date +'.jpg')
            time.sleep(1)
        camera.close()
        for fileName in os.listdir(directory):
            if fileName.endswith('.jpg'):
                filePath = os.path.join(directory, fileName) # joins directory path with filename to create file's full path
                fileList.append(filePath)
                detect(filePath)
        result = identify(faceIdList)
        if result[0][1] > .5: # if confidence is greater than .7 get name of person
            user = getName(result[0][0])
            if user.blacklisted == False:
                passs()
                break
            else:
                fail()
                break
            
        else:
           isRecognizing = False
           fail()
           break

def log_event(user, status):
    event_id = str(uuid.uuid4().hex)
    event = Event(event_id=event_id, owner=user, status=status)
    db.session.add(event)
    db.session.commit()

@app.route("/passs", methods=["GET"])
def passs():
    passs()
    return jsonify({"status":"200"})

@app.route("/fail", methods=["GET"])
def fail():
    fail()
    return jsonify({"status":"200"})

def train():
    params = urllib.urlencode({'personGroupId': group_id})
    headers = {'Ocp-Apim-Subscription-Key': KEY}

    conn = http.client.HTTPSConnection('westcentralus.api.cognitive.microsoft.com')
    conn.request("POST", "/face/v1.0/persongroups/"+group_id+"/train?%s" % params, "{body}", headers)
    response = conn.getresponse()
    #data = json.loads(response.read())
    print(response.read()) # if successful prints empty json body

        



@app.route("/hello")
def hello():
    return "Hello World!"

@app.route("/user/create", methods=["POST"])
def create_user():
    user_id = str(uuid.uuid4().hex)
    username = request.json['username']
    email = request.json['email']
    phone = request.json['phone']
    email = request.json['email']
    address = request.json['address']
    blacklisted = False
    new_user = User(user_id=user_id,username=username, email=email, phone=phone, address=address, blacklisted=blacklisted)
    
    
    headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': KEY}
    params = urllib.urlencode({'personGroupId': group_id})
    conn = http.client.HTTPSConnection('westcentralus.api.cognitive.microsoft.com')
    body = "{'name':'"+new_user.username+"'}"
    conn.request("POST", "/face/v1.0/persongroups/{"+group_id+"}/persons?%s" % params, body, headers)
    response = conn.getresponse()
    data = json.loads(response.read()) # turns response into index-able dictionary
    print(data)
    azure_id = data['personId']
    
    new_user.azure_id = azure_id
    db.session.add(new_user)
    db.session.commit()
    user = user_schema.dump(new_user)
    
    conn.close()
    
    return jsonify(user.data)


# endpoint to get one user
@app.route("/user/<id>", methods=["GET"])
def get_user(id):
    user = db.session.query(User).filter(User.user_id==id).first()
    result = user_schema.dump(user)
    return jsonify(result)


# endpoint to upload photos of the user
@app.route("/upload", methods=["POST"])
def upload():
    headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key':KEY}
    conn = http.client.HTTPSConnection('westcentralus.api.cognitive.microsoft.com')
    photos = UploadSet('photos',IMAGES)
    folderUri = 'files/photos/'+request.form['username']
    user_id = request.form['user_id']
    app.config['UPLOADED_PHOTOS_DEST'] = folderUri
    configure_uploads(app, photos)
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        photoUrl=folderUri+'/'+filename
        user = db.session.query(User).filter(User.user_id==user_id).first()
        
        params = urllib.urlencode({'personGroupId': group_id, 'personId': user.azure_id}) # item[1] is the personId created from addPeople()
        
        avatar_id = str(uuid.uuid4().hex)
        a = Avatar(avatar_id = avatar_id, avatar_url = photoUrl, user=user)
        #user.avatars.append(a)f
        db.session.add(a)
        #db.session.add(user)
        db.session.commit()
##        return jsonify({'photoUrl':photoUrl})
        filePath = os.path.join(folderUri, filename)
        body = open(filePath,'rb')
        conn.request("POST", "/face/v1.0/persongroups/{"+user.azure_id+"}/persons/"+user.azure_id+"/persistedFaces?%s" % params, body, headers)
        response = conn.getresponse()
        data = json.loads(response.read()) # successful run will print persistedFaceId
        print(data)
        train()
        return jsonify({'avatar':a.avatar_id})
    else:
        return ({'error':'Please upload a file'})

@app.route("/group/create", methods=["POST"])
def create_group():
    body = '{"name": "users"}'
    params = urllib.urlencode({'personGroupId': group_id})
    headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': KEY}
    conn = http.client.HTTPSConnection('westcentralus.api.cognitive.microsoft.com')
    conn.request("PUT", "/face/v1.0/persongroups/{personGroupId}?%s" % params, body, headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    return jsonify(data)
    conn.close()



if __name__ == '__main__':
    app.run(host='0.0.0.0')
