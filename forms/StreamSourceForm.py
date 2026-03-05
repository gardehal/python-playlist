from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class StreamSourceForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(0, 200)])
    uri = StringField("URI", validators=[Length(0, 200)])
    isWeb = BooleanField("Is web", default=False)
    streamSourceTypeId = IntegerField("Type", validators=[NumberRange(1)])
    enableFetch = BooleanField("Enable fetch", default=False)
    backgroundContent = BooleanField("Background content", default=False)
    alwaysDownload = BooleanField("Always download", default=False)
    
    submit = SubmitField("Save")
    # cancel = SubmitField("Cancel")
