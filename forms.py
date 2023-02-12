from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, validators
from flask_ckeditor import CKEditorField

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField(label="Blog Post Title", validators=[validators.DataRequired()])
    subtitle = StringField(label="Subtitle", validators=[validators.DataRequired()])
    img_url = StringField(label="Blog Image URL", validators=[validators.DataRequired(), validators.URL()])
    body = CKEditorField(label="Blog Content", validators=[validators.DataRequired()])
    submit = SubmitField(label="Submit Post")

#WTForm for register
class RegisterForm(FlaskForm):
    email = EmailField(label="Email", validators=[validators.DataRequired(), validators.Email()])
    password = StringField(label="Password", validators=[validators.DataRequired()])
    name = StringField(label="Name", validators=[validators.DataRequired()])
    submit = SubmitField("Sign me up!")

#WTForm for register
class LoginForm(FlaskForm):
    email = EmailField(label="Email", validators=[validators.DataRequired(), validators.Email()])
    password = StringField(label="Password", validators=[validators.DataRequired()])
    submit = SubmitField("Let me in!")

#WTForm for comments
class CommentForm(FlaskForm):
    body = CKEditorField(label="Comment", validators=[validators.DataRequired()])
    submit = SubmitField("Submit comment")