from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, URL

class YoutubePlaylistForm(FlaskForm):
    url = StringField('YouTube Playlist URL *', validators=[DataRequired(), URL()])
    name = StringField('Name', render_kw={'placeholder': 'Defaults to playlist name from YouTube'})
    description = StringField('Description')
    playWatchedStreams = BooleanField('Play Watched Streams')
    allowDuplicates = BooleanField('Allow Duplicates')
    favorite = BooleanField('Favorite')
    sortOrder = IntegerField('Sort Order')
    submit = SubmitField('Create Playlist')
