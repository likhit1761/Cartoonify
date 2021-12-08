from flask import Flask, redirect, request, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
import os
from Cartoon import cartoonify

app = Flask(__name__)
app.secret_key = 'secret key'

basedir = os.path.abspath(os.path.dirname(__file__))
UPLOADED_PHOTOS_DEST = os.path.join(basedir, 'static', 'uploads')

cartoon_choices = [('1', 'Black&White'), ('2', 'Sketch'), ('3', 'Painting'),('4','WitchFiltered')]


class PhotoForm(FlaskForm):
    photo = FileField('Choose image',
                      validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'], "Only images are allowed")])
    select = SelectField('Select the choice of image', choices=cartoon_choices)
    submit = SubmitField("Submit")


@app.route('/', methods=['GET', 'POST'])
def initial():
    form = PhotoForm()
    print('Server running')
    if request.method == 'GET':
        return render_template('index.html', form=form)
    else:
        if form.validate_on_submit():
            f = form.photo.data
            try:
                os.remove(os.path.join(UPLOADED_PHOTOS_DEST, secure_filename(f.filename)))
                print('deleted file')
            except:
                print('new file')
            finally:
                f.save(os.path.join(UPLOADED_PHOTOS_DEST, secure_filename(f.filename)))
                cartoonify(f.filename, dict(cartoon_choices).get(form.select.data))
                print(f.filename)
                return redirect(url_for('result', filename=f.filename))
        else:
            return render_template('index.html', form=form)


@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'GET':
        return render_template('preview.html',
                               filename=request.args.get('filename'))
    else:
        return redirect(url_for('initial'))


if __name__ == '__main__':
    app.run(debug=True)
