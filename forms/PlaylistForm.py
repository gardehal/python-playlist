from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class PlaylistForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(0, 200)])
    description = StringField("Description", validators=[Length(0, 200)])
    sortOrder = IntegerField("Sort order", validators=[NumberRange(0)], default=99)
    playWatchedStreams = BooleanField("Play watched streams", default=False)
    allowDuplicates = BooleanField("Allow duplicates", default=False)
    favorite = BooleanField("Favorite", default=False)
    
    submit = SubmitField("Save")
    # cancel = SubmitField("Cancel")
