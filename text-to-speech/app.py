#Import the Libraries
import boto3
from flask import Flask, render_template, request, redirect, url_for, session, send_file, Response, abort
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import sys
import os, time
import uuid

#Initialise the variables
app = Flask(__name__)
app.secret_key = 'axnasavqwdqwjdqz'
file_path = os.path.join(os.getcwd(),"static","Speech Storage")
polly = boto3.client('polly')

#Home page
@app.route('/', methods=["GET", "POST"])
def index():

    #Clean the mp3 files stored at the server side if the file is more than half an hour old (3600 seconds).
    def garbage_cleaning():
        now = time.time()

        for f in os.listdir(file_path):
            f = os.path.join(file_path,f)
            if os.stat(f).st_mtime < now - 3600:
                if os.path.isfile(f):
                    os.remove(f)

    #fetch() will take the text input, forward it to amazon polly and get the response back and finally write to a temporary
    #mp3 file in the Speech Storage folder.
    def fetch():

        #create a session variable everytime there's a fetch request and this will be a random string that will be used to
        #store our file
        session["valid"] = str(uuid.uuid4())

        #get the text input
        text_input = request.form.get("text_input")

        try:

            #forward it to polly
            response = polly.synthesize_speech(Text=text_input, OutputFormat="mp3", VoiceId="Joanna")

        except (BotoCoreError, ClientError) as error:
            print(error)
            sys.exit(-1)

        #Access the audio stream from the response
        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                output = os.path.join(file_path, session["valid"]+"-"+"speech-ict.mp3")
                try:
                    #Open a file for writing the output as a binary stream
                    with open(output, "wb") as file:
                        file.write(stream.read())
                except IOError as error:
                    #Could not write to file, exit gracefully
                    print(error)
                    sys.exit(-1)

        else:
            # The response didn't contain audio data, exit gracefully
            print("Could not stream audio")
            sys.exit(-1)


    if request.form.get("fetch"):
        fetch()

    elif request.form.get("play"):

        #check if the person has clicked on the fetch button before pressing the play button in this session.
        #Note: session variables are auto-deleted by flask when the user closes the browser. Hence, session is the period
        #      between person accessing the site and him closing the browser.

        if "valid" in session.keys():
            return redirect(url_for("speech_audio"))
        else:
            abort(404, description="First provide an input and press the fetch button")

    elif request.form.get("download"):

        #same check for download
        if "valid" in session.keys():
            return send_file(os.path.join(file_path, session["valid"] + "-" + "speech-ict.mp3"), as_attachment=True)
        else:
            abort(404, description="First provide an input and press the fetch button")

    #run garbage cleaning everytime the page is rendered.
    garbage_cleaning()
    return render_template("home.html")

#play request will be forwarded here
@app.route("/speech_audio",methods=["GET","POST"])
def speech_audio():

    #person tries to directly hit the endpoint without ever going to the home page.
    if "valid" not in session.keys():
        abort(404)

    output = os.path.join(file_path,session["valid"]+"-"+ "speech-ict.mp3")

    #playing is the real-time streaming of bytes of data (hence we use generator for this to generate or yield the bytes)
    def generate():
        with open(output, "rb") as fmp3:
            data = fmp3.read(1024)
            while data:
                yield data
                data = fmp3.read(1024)

    return Response(generate(), mimetype="audio/mpeg")


if __name__ == '__main__':
    app.run(host="0.0.0.0")
