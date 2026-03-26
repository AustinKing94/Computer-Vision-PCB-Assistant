import os
from distutils.log import debug
from fileinput import filename
from flask import *  


UPLOAD_FOLDER = '/Users/austinking/Documents/CurrentCourseWork/COMP-4983/finalProject/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')  
def main():  
    return render_template("dashboard.html")  

@app.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':  
        f = request.files['file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
        return render_template("Acknowledgement.html", name = f.filename)  

if __name__ == '__main__':  
    app.run(debug=True)