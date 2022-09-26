import boto3
from flask import Flask, render_template, request, redirect, url_for, session, send_file, Response, abort
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import sys
import os, time
import uuid

app = Flask(__name__)
app.secret_key = 'axnasavqwdqwjdqz'
file_path = r"static\Speech Storage"
polly = boto3.client('polly')

@app.route('/', methods=["GET", "POST"])
def index():
    def garbage_cleaning():
        now = time.time()

        for f in os.listdir(file_path):
            f = os.path.join(file_path,f)
            if os.stat(f).st_mtime < now - 3600:
                if os.path.isfile(f):
                    os.remove(f)

    def fetch():
        session["valid"] = str(uuid.uuid4())

        text_input = request.form.get("text_input")
        try:
            response = polly.synthesize_speech(Text=text_input, OutputFormat="mp3", VoiceId="Joanna")
        except (BotoCoreError, ClientError) as error:
            print(error)
            sys.exit(-1)

        # Access the audio stream from the response
        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                output = os.path.join(file_path, session["valid"]+"-"+"speech-ict.mp3")
                try:
                    # Open a file for writing the output as a binary stream
                    with open(output, "wb") as file:
                        file.write(stream.read())
                except IOError as error:
                    # Could not write to file, exit gracefully
                    print(error)
                    sys.exit(-1)

        else:
            # The response didn't contain audio data, exit gracefully
            print("Could not stream audio")
            sys.exit(-1)


    if request.form.get("fetch"):
        fetch()

    elif request.form.get("play"):
        if "valid" in session.keys():
            return redirect(url_for("speech_audio"))
        else:
            abort(404, description="First provide an input and press the fetch button")

    elif request.form.get("download"):
        if "valid" in session.keys():
            return send_file(os.path.join(file_path, session["valid"] + "-" + "speech-ict.mp3"), as_attachment=True)
        else:
            abort(404, description="First provide an input and press the fetch button")

    garbage_cleaning()
    return render_template("home.html")

@app.route("/speech_audio",methods=["GET","POST"])
def speech_audio():

    if "valid" not in session.keys():
        abort(404)
    print("In speech")
    output = os.path.join(file_path,session["valid"]+"-"+ "speech-ict.mp3")

    def generate():
        with open(output, "rb") as fmp3:
            data = fmp3.read(1024)
            print(data)
            while data:
                yield data
                data = fmp3.read(1024)

    return Response(generate(), mimetype="audio/mpeg")


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=80)