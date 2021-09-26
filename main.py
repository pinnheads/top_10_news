from os import environ
from flask.helpers import flash, url_for
from werkzeug.utils import redirect
from prepare_news import PrepareNews
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)

app.config["SECRET_KEY"] = environ["KEY"]
news = PrepareNews()
Bootstrap(app)


class EmailForm(FlaskForm):
    email = StringField("", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")


@app.route("/", methods=["GET", "POST"])
def home():
    form = EmailForm()

    if request.method == "POST" and form.validate_on_submit():
        user_email = form.email.data
        with open("user_emails.csv", "a+") as emails_csv:
            emails_csv.write(f"{user_email}\n")
            flash(
                message="Your email was saved successfully! Thank you for signing up.",
                category="info",
            )
            return redirect(url_for("home"))

    # top_10_news = news.create_news()
    # print(top_10_news)
    return render_template("index.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
