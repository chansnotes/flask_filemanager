from flask import Flask, render_template, redirect, request, send_file, abort
from flask_wtf.csrf import CSRFProtect
from flask.helpers import send_from_directory
from flask_fontawesome import FontAwesome
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, DateTimeField, BooleanField, TextAreaField, TelField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired
import os
import subprocess
import sys
import filetype
from datetime import datetime
from hurry.filesize import size

app = Flask(__name__)
fa = FontAwesome(app)

app.config['SECRET_KEY'] = 'hahahoho'

currentDirectory = '/home/test'

tp_dict = {'image': 'image.png', 'video': 'mp4.png'}
maxNameLength = 15


class createNewDirectory(FlaskForm):

    dir_name = StringField('Please type the name of folder',
                           validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def root():
    curr_dir = os.getcwd()
    file_list = subprocess.check_output(
        'ls', shell=True).decode('utf-8').split('\n')
    dList = list(os.listdir('.'))
    dList = list(filter(lambda x: os.path.isdir(x), os.listdir('.')))
    fList = list(filter(lambda x: not os.path.isdir(x), os.listdir('.')))
    dir_list_dict = {}
    file_list_dict = {}

    for i in dList:
        image = 'folder.png'
        if len(i) > maxNameLength:
            dots = "..."
        else:
            dots = ""

        dir_stats = os.stat(i)
        dir_list_dict[i] = {}
        dir_list_dict[i]['f'] = i[0:maxNameLength]+dots
        dir_list_dict[i]['f_url'] = i
        dir_list_dict[i]['currentDir'] = curr_dir
        dir_list_dict[i]['image'] = image
        dir_list_dict[i]['dtc'] = datetime.utcfromtimestamp(
            dir_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        dir_list_dict[i]['dtm'] = datetime.utcfromtimestamp(
            dir_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        dir_list_dict[i]['size'] = "---"

    for i in fList:
        image = None
        try:
            kind = filetype.guess(i)
            if kind:
                tp = kind.mime.split('/')[0]

                if tp in tp_dict:
                    image = tp_dict[tp]
        except:
            pass

        if not image:
            image = 'file_icon.png'

        if len(i) > maxNameLength:
            dots = "..."
        else:
            dots = ""

        file_list_dict[i] = {}
        file_list_dict[i]['f'] = i[0:maxNameLength]+dots
        file_list_dict[i]['f_url'] = i
        file_list_dict[i]['currentDir'] = curr_dir
        file_list_dict[i]['f_complete'] = i
        file_list_dict[i]['image'] = image

        try:
            dir_stats = os.stat(i)
            file_list_dict[i]['dtc'] = datetime.utcfromtimestamp(
                dir_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            file_list_dict[i]['dtm'] = datetime.utcfromtimestamp(
                dir_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            file_list_dict[i]['size'] = size(dir_stats.st_size)
        except:
            file_list_dict[i]['dtc'] = "---"
            file_list_dict[i]['dtm'] = "---"
            file_list_dict[i]['size'] = "---"

    form = createNewDirectory()
    return render_template('index.html', curr_dir=curr_dir, file_list=file_list, form=form,  dir_list_dict=dir_list_dict, file_list_dict=file_list_dict)

# Move to the selected directory


@app.route('/cd')
def cd():
    os.chdir(request.args.get('path'))
    return redirect('/')


@app.route('/view')
def view():
    # Get the file content
    # content = subprocess.check_output(
    #     'cat ' + request.args.get('file'), shell=True).decode('utf-8').replace('\n', '<br>')
    # return content
    with open(request.args.get('file')) as f:
        return f.read().replace('\n', '<br>')


@app.route('/image')
def image():
    # send_file = Insecure method of sending a single file, May become a target of attack
    # return send_file(request.args.get('file'), mimetype='image/jpg')

    # send_from_directory = Check whether reqeusted file is really from specified directory.
    try:
        return send_from_directory(directory=request.args.get('path'), filename=request.args.get('filename'), mimetype='image/jpg')
    except FileNotFoundError:
        abort(404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
