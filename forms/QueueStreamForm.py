from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import Length, Optional

class QueueStreamForm(FlaskForm):
    name = StringField("Name", validators=[Length(0, 200)], render_kw={'placeholder': 'Optional: URI title on create; current name on edit'})
    uri = StringField("URI", validators=[Length(0, 200)])
    isWeb = BooleanField("Is web", default=False)
    streamSourceId = StringField("StreamSource ID", validators=[Length(0, 200)])
    streamSourceName = StringField("StreamSource Name", validators=[Length(0, 200)])
    watched = BooleanField("Watched", default=False)
    backgroundContent = BooleanField("Background content", default=False)
    playtimeSeconds = IntegerField("Playtime in seconds", validators=[Optional()], render_kw={'placeholder': 'Defaults to 0'})
    remoteId = StringField("Remote ID", validators=[Length(0, 200)])
    
    submit = SubmitField("Save")
    # cancel = SubmitField("Cancel")
