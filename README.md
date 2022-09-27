# Text-to-Speech

# Where is the website?
http://ec2-18-220-63-153.us-east-2.compute.amazonaws.com:5000/

# What does the website do?
1. It takes in a text and outputs a Text-to-Speech file (tts) using Amazon Polly.

# How to use the website?
1. You have to enter the text and click on the "Fetch speech" button (by default the entered text is "Enter text" so make sure to delete it!).
2. In order to play or download the tts file, you need to click on the fetch speech button
3. You cannot play or download the tts file without pressing the fetch speech button at least once.

#How to access the code?
1. In the Text-to-Speech repo, there's a folder called text-to-speech.
2. In that, there is an app.py file which has the Flask code.
3. Along with the py file, there are 2 other folders - static (which contains the temporary storage folder called Speech Storage and the styles folder which has the css folder containing the styles.css file) and templates (which contains the home.html file)
