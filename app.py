from flask import Flask, render_template, request, redirect, url_for
from flask import session
from flask_login import LoginManager

from models import db




app = Flask(__name__)
app.secret_key = "kamni2528"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://PC:2819874@localhost:3306/mytestdb'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

from models import User, Request, RequestHistory, RequestStatus  # noqa

with app.app_context() as context:
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("profile"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Проверяем, что пользователь с таким email еще не зарегистрирован
        if User.query.filter_by(email=email).first() is not None:
            return render_template("register.html", error="Пользователь с таким email уже зарегистрирован")

        # Генерируем хеш пароля и сохраняем его в базу данных
        user = User(name=name, email=email, password=password)

        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        return redirect(url_for("profile"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Ищем пользователя с таким email в базе данных
        user = User.query.filter_by(email=email).first()
        print("user:", user)
        if user is None:
            # Return 404 or 500
            ...

        if user.check_password(password):
            print("User valid")
            session["user_id"] = user.id
            return redirect(url_for("profile"))
        else:
            return render_template("login.html", error="Неправильный email или пароль")

    return render_template("login.html")















@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()
    solvers = User.query.filter_by(role="solver").all()

    return render_template("profile.html", user=user, solvers=solvers)


@app.route("/my_requests")
def my_requests():
    user = User.query.filter_by(
        id=session["user_id"]
    ).first()

    user_requests = user.opened_requests
    solvers = User.query.filter_by(role="solver").all()

    return render_template("my_requests.html", requests=user_requests, solvers=solvers)


@app.route("/new_request", methods=["GET", "POST"])
def new_request():
    if request.method == "POST":
        problem_title = request.form["problem_title"]
        problem_description = request.form["problem_description"]
        solver = request.form["solver"]

        _request = Request(problem_title, problem_description, int(solver), session["user_id"])

        db.session.add(_request)
        db.session.commit()

        request_history = RequestHistory(
            _request.id,
            session["user_id"],
            1,
            description=f"Request Opened."
        )

        db.session.add(request_history)
        db.session.commit()

        return redirect(url_for("my_requests"))

    solvers = User.query.filter_by(role="solver").all()

    return render_template("create_request.html", solvers=solvers)


@app.route("/requests/<request_id>/update_status", methods=["POST"])
def update_request_status(request_id: int):
    if request.method == "POST":
        status = request.form["status"]

        request_status: RequestStatus = RequestStatus.query.filter_by(status_name=status).first()

        if request_status is None:
            # TODO: RETURN 404 PAGE
            return redirect(url_for("index"))

        _request: Request = Request.query.filter_by(id=request_id).first()

        if _request is None:
            # TODO: RETURN 404 PAGE
            return redirect(url_for("index"))

        _request.status = status

        request_history = RequestHistory(
            request_id,
            session["user_id"],
            request_status.status_id,
            description=f"Request {request_status.status_name}."
        )

        db.session.add(request_history)
        db.session.commit()

        return redirect(url_for("my_requests"))


@app.route("/requests/<request_id>/edit", methods=["POST"])
def update_request_details(request_id: int):
    if request.method == "POST":
        _request: Request = Request.query.filter_by(id=request_id).first()

        if _request is None:
            # TODO: RETURN 404 PAGE
            return redirect(url_for("index"))

        problem_title = request.form["problem_title"]
        problem_description = request.form["problem_description"]
        solver_id = request.form["solver"]

        _request.title = problem_title
        _request.description = problem_description
        _request.solver_id = solver_id

        db.session.commit()

        return redirect(url_for("my_requests"))


@app.route("/requests/<request_id>/view", methods=["GET"])
def view_request_details(request_id: int):
    if request.method == "GET":
        _request: Request = Request.query.filter_by(id=request_id).first()

        if _request is None:
            # TODO: RETURN 404 PAGE
            return redirect(url_for("index"))

        solvers = User.query.filter_by(role="solver").all()

        return render_template("request_info.html", solvers=solvers, _request=_request)


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))
