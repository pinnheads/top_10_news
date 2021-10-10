import smtplib
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
system_key = environ["EMAIL_KEY"]
news = PrepareNews()
Bootstrap(app)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = environ.get(
    "DATABASE_URL", "sqlite:///blog.db"
)
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


def get_10_news():
    top_10_news = news.create_news()
    msg = ""
    for get_news in top_10_news:
        news_text = (get_news["a_text"]).decode("utf-8", "strict")
        news_link = (get_news["a_link"]).decode("utf-8", "strict")
        news_msg = news_text + "\n" + news_link + "\n\n"
        msg += news_msg

    return msg


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

    return render_template("unsubscribe.html", form=form)


smtp_email = environ["MY_SMTP_EMAIL"]
password = environ["MY_SMTP_PASSWORD"]


@app.route("/send_mail/<secret_key>")
def send_mail(secret_key):
    news = get_10_news()
    email_text = "Subject:Daily News\n\n"
    email_text += news
    all_users = db.session.query(User).all()
    if secret_key == system_key:
        for user in all_users:
            if news != "":
                with smtplib.SMTP("smtp.gmail.com") as connection:
                    print("Connection Established")
                    connection.starttls()
                    connection.login(user=smtp_email, password=password)
                    connection.sendmail(
                        from_addr=smtp_email,
                        to_addrs=user.email,
                        msg=email_text,
                    )
                print(f"Email sent to {user.email} from {smtp_email}")
            else:
                print("Something went wrong")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
