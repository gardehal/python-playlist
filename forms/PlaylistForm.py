from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class PlaylistForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(0, 40)])
    description = StringField("Description", validators=[Length(0, 100)])
    sortOrder = IntegerField("Sort order")
    playWatchedStreams = BooleanField("Play watched streams", default=False)
    allowDuplicates = BooleanField("Allow duplicates", default=False)
    favorite = BooleanField("Favorite", default=False)
    
    submit = SubmitField("Save")
