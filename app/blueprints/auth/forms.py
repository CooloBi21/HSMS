from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Tên đăng nhập", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Mật khẩu", validators=[DataRequired()])
    submit = SubmitField("Đăng nhập")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Mật khẩu hiện tại", validators=[DataRequired()])
    new_password = PasswordField("Mật khẩu mới", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Đổi mật khẩu")
