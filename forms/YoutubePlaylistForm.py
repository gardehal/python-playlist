from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL

class YoutubePlaylistForm(FlaskForm):
    url = StringField('YouTube Playlist URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Create Playlist')
