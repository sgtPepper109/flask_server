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


# Get information (features) of all videos
@app.route('/getVideoStats')
def getVideoStats():
    global video_store

    # response object (array)
    video_info_array = list()

    # for all the videos in the video store
    for i in video_store:
        # to add this to the array of responses
        video_info = {
            'filename': video_store[i]['file_name'],
            'file_extension': video_store[i]['file_extension'],
            'title': video_store[i]['title'],
            'id': i,
            'subtitles_file': video_store[i]['subtitle_location'],
        }
        video_info_array.append(video_info)
    
    # send response
    return make_response(video_info_array)


# get the video to render on the client page
# request parameter: id
@app.route('/getVideo')
def getVideo():
    global video_store

    # parse request parameters
    args = request.args.to_dict()
    # get id from request parameters
    id = int(args['id'])

    # get video file location/path (saved in assets) (This is stored in 'video_store' variable)
    file_location_to_send = video_store[id]['location']
    # similarly get file_name
    file_name = video_store[id]['file_name']
    # similarly get file_extension
    file_extension = video_store[id]['file_extension']
    
    # return video file with the help of 'send_file' method in flask
    return send_file(file_location_to_send, download_name=file_name, mimetype="video/" + file_extension)


# get subtitles file to show in client page
# request parameter: id
@app.route('/getSubtitles')
def getSubtitles():
    global video_store

    # parse request parameter
    args = request.args.to_dict()
    # get id from request parameters
    id = int(args['id'])

    # get subtitles file location/path (saved in assets) (This is stored in 'video_store' variable)
    subtitles_file_location_to_send = video_store[id]['subtitle_location']
    # return subtitles file with the help of 'send_file' method in flask
    return send_file(subtitles_file_location_to_send)


# Just a test (Home) route
@app.route('/')
def test():
    return 'TOUCHCORE ASSESSMENT FLASK SERVER. Name: Abdulrahim Shaikh'


if __name__ == "__main__":
    # When server is started/restarted, clear the database (Assets folder)
    for filename in os.listdir(assets_location):
        file_path = os.path.join(assets_location, filename)
        os.remove(file_path)
    
    # Run server (public)
    app.run(debug=False, host='0.0.0.0')
    # app.run()
