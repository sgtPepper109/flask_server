import os
import shutil
import sys
from flask import Flask, make_response, request, send_file
from flask_cors import CORS
import requests

app = Flask(__name__)
cors = CORS(app)

# instead of using a database, all the details of the videos saved in Assets will be stored in this variable
video_store = dict()
unique_id = 0
current_video_upload_id = 0

# Assets folder location which contains all uploaded videos
assets_location = './Assets/'

@app.route("/upload_file", methods=['POST'])
def upload_file():
    global video_store
    global unique_id
    global current_video_upload_id

    # parse request parameters from url (which contains filename)
    args = request.args.to_dict()

    # filename parameter
    file_name = args['filename']
    file_extension = file_name.split('.')[-1]

    # video title parameter
    video_title = args['title']
    video_title = video_title.replace('%20', ' ')

    # file to be saved to this location (Assets folder)
    file_save_location = assets_location + file_name

    # if there exists a file with this name, then 
    if (os.path.isfile(file_save_location)):
        return make_response('File already exists')

    # else:
    # write (binary) video data received from frontend to the video file to be saved in Assets
    with open(file_save_location, "wb") as out_file:
        # request.data holds the raw video file data
        out_file.write(request.data)
    
    # unique id must be unique. Hence auto incremented value will be used to store the details
    unique_id += 1
    video_store[unique_id] = {
        'file_name': file_name,
        'file_extension': file_extension,
        'location': file_save_location,
        'title': video_title
    }
    current_video_upload_id = unique_id
    
    # send acknowledgement response
    return make_response('Video saved successfully')
    # return send_filo_file_save_location, download_name=file_name, mimetype="video/" + file_extension)


@app.route("/uploadVtt", methods=['POST'])
def uploadVtt():
    global video_store
    global unique_id
    global current_video_upload_id

    # parse request parameters from url (which contains filename)
    args = request.args.to_dict()

    # filename parameter
    vtt_file_name = args['filename']

    # file to be saved to this location (Assets folder)
    vtt_file_save_location = assets_location + vtt_file_name
    video_store[unique_id]['subtitle_location'] = vtt_file_save_location

    # if there exists a file with this name, then 
    if (os.path.isfile(vtt_file_save_location)):
        return make_response('File already exists')

    # else:
    # write (binary) video data received from frontend to the video file to be saved in Assets
    with open(vtt_file_save_location, "wb") as out_file:
        # request.data holds the raw video file data
        out_file.write(request.data)
    
    
    # send acknowledgement response
    # return send_filo_file_save_location, download_name=file_name, mimetype="video/" + file_extension)
    print(video_store)
    return make_response('Subtitles saved successfully')


@app.route('/getVideoStats')
def getVideoStats():
    global video_store
    video_info_array = list()
    for i in video_store:
        video_info = {
            'filename': video_store[i]['file_name'],
            'file_extension': video_store[i]['file_extension'],
            'title': video_store[i]['title'],
            'id': i,
            'subtitles_file': video_store[i]['subtitle_location'],
        }
        video_info_array.append(video_info)
    return make_response(video_info_array)


@app.route('/getSampleVideo')
def getSampleVideo():
    return send_file('./Assets/video1.mp4', download_name='video1.mp4', mimetype="video/mp4")


@app.route('/getVideo')
def getVideo():
    global video_store
    args = request.args.to_dict()
    id = int(args['id'])
    file_location_to_send = video_store[id]['location']
    file_name = video_store[id]['file_name']
    file_extension = video_store[id]['file_extension']
    return send_file(file_location_to_send, download_name=file_name, mimetype="video/" + file_extension)


@app.route('/getSubtitles')
def getSubtitles():
    global video_store
    args = request.args.to_dict()
    id = int(args['id'])
    subtitles_file_location_to_send = video_store[id]['subtitle_location']
    return send_file(subtitles_file_location_to_send)

if __name__ == "__main__":
    for filename in os.listdir(assets_location):
        file_path = os.path.join(assets_location, filename)
        os.remove(file_path)
    app.run()
