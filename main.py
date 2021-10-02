from os import environ
from flask.helpers import flash, url_for
from werkzeug.utils import redirect
from prepare_news import PrepareNews
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)

app.config["SECRET_KEY"] = environ["KEY"]
news = PrepareNews()
Bootstrap(app)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user_emails.db"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)

    def __repr__(self):
        return "<Title %r>" % self.title


class EmailForm(FlaskForm):
    email = StringField("", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")


class UnsubscribeEmailForm(FlaskForm):
    email = StringField("", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")


db.create_all()


@app.route("/", methods=["GET", "POST"])
def home():
    form = EmailForm()

    if request.method == "POST" and form.validate_on_submit():
        user_email = form.email.data
        new_user = User(email=user_email)
        db.session.add(new_user)
        db.session.commit()
        flash(
            message="Your email was saved successfully! Thank you for signing up.",
            category="info",
        )
        return redirect(url_for("home"))

    # top_10_news = news.create_news()
    # print(top_10_news)
    return render_template("index.html", form=form)


@app.route("/unsubscribe", methods=["GET", "POST"])
def unsubscribe():
    form = UnsubscribeEmailForm()

    if request.method == "POST" and form.validate_on_submit():
        user_email = form.email.data
        email_to_delete = User.query.filter_by(email=user_email).first()
        if email_to_delete:
            db.session.delete(email_to_delete)
            db.session.commit()
            flash(
                message="Your email was removed from the mailing list.",
                category="info",
            )
            return redirect(url_for("unsubscribe"))
        else:
            flash(
                message="Your email was not found",
                category="error",
            )
            return redirect(url_for("home"))

    return render_template("index.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
