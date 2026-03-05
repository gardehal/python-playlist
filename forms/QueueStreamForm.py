from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class QueueStreamForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(0, 200)])
    uri = StringField("URI", validators=[Length(0, 200)])
    isWeb = BooleanField("Is web", default=False)
    streamSourceId = StringField("StreamSource ID", validators=[Length(0, 200)])
    streamSourceName = StringField("StreamSource Name", validators=[Length(0, 200)])
    watched = BooleanField("Watched", default=False)
    backgroundContent = BooleanField("Background content", default=False)
    playtimeSeconds = IntegerField("Playtime in seconds", validators=[Optional()])
    remoteId = StringField("Remote ID", validators=[Length(0, 200)])
    
    submit = SubmitField("Save")
    # cancel = SubmitField("Cancel")
