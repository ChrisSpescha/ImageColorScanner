from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'superserial'
app.config['UPLOAD_PATH'] = 'image'
Bootstrap(app)


class UploadPhoto(FlaskForm):
    image = FileField("Upload Image", validators=[DataRequired()])
    submit = SubmitField("Create Palette")


@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadPhoto()
    img = os.listdir(app.config['UPLOAD_PATH'])
    img_address = "image/" + img[0]
    img_obj = Image.open(img_address)

    if img_obj.format != "JPG":
        img_obj = img_obj.convert("RGB")
    img_array = np.array(img_obj)
    unique, counts = np.unique(img_array.reshape(-1, 3), axis=0, return_counts=True)
    colors_list = []

    for i in range(10):
        highest_index = np.argmax(counts)
        color = unique[highest_index]
        colors_list.append(color)
        counts = np.delete(counts, [highest_index])

    if request.method == "POST":
        if form.validate_on_submit():
            for f in os.listdir(app.config['UPLOAD_PATH']):
                os.remove(os.path.join(app.config['UPLOAD_PATH'], f))
            uploaded_file = form.image.data
            filename = secure_filename(uploaded_file.filename)
            if filename != '':
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                return redirect(url_for('index'))

    return render_template('index.html', img=img_address, form=form, colors=colors_list)


@app.route('/image/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


if __name__ == "__main__":
    app.run(debug=True)
