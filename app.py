import os
from distutils.log import debug
from fileinput import filename
from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Renders the main dashboard UI"""
    return render_template('dashboard.html')

@app.route('/gallery')
def gallery():
    """Renders the gallery UI"""
    return render_template('gallery.html')

@app.route('/get_current_image')
def get_current_image():
    """
    Placeholder route for the camera feed. 
    Currently redirects to a dummy image so you can see how the UI frames it.
    Later, this will return your processed OpenCV/ArUco frames.
    """
    return redirect("https://via.placeholder.com/800x450.png?text=Camera+Feed+Offline")

if __name__ == '__main__':
    # host='0.0.0.0' makes the server accessible to other devices on your local network.
    # This is perfect for running the app on your Raspberry Pi and viewing the UI on your laptop.
    app.run(debug=True, host='0.0.0.0', port=8080)