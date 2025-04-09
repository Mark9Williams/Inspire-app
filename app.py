from cs50 import SQL
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session, redirect, flash, url_for, jsonify
from flask_session import Session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///inspire.db")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Login is required to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def landing():
    return render_template("landingpage.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            flash("Username is blank")
            return redirect(url_for("register"))
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password or not confirmation or password != confirmation:
            flash("Either input is blank or passwords do not match")
            return redirect(url_for("register"))
        email = request.form.get("email")
        if not email:
            flash("Email is blank")
            return redirect(url_for("register"))
        try:
            password = generate_password_hash(password)
            db.execute("INSERT INTO users(username, email, password) VALUES(?, ?, ?)", username, email, password)
        except ValueError:
            flash("Name already taken")
            return redirect(url_for("register"))
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("User name not provided")
            return redirect(url_for("login"))

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Password not provided")
            return redirect(url_for("login"))

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password"], request.form.get("password")
        ):
            flash("Invalid username and/or password")
            return redirect(url_for("login"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect(url_for("dashboard"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("index.html")


@app.route("/search", methods=["GET"])
@login_required
def search():
    query = request.args.get("q")
    if query:
        user = db.execute("SELECT * FROM users WHERE username = ?", query)
        if len(user) == 1:
            books = db.execute("SELECT * FROM books_read WHERE user_id = ?", user[0]["id"])
            projects = db.execute("SELECT * FROM projects WHERE user_id = ?", user[0]["id"])
            hobbies = db.execute("SELECT * FROM hobbies WHERE user_id = ?", user[0]["id"])
            possessions = db.execute("SELECT * FROM possessions WHERE user_id = ?", user[0]["id"])
            networth = db.execute("SELECT * FROM networth WHERE user_id = ?", user[0]["id"])
            jobs = db.execute("SELECT * FROM jobs WHERE user_id = ?", user[0]["id"])
            book_recommendations = db.execute("SELECT * FROM book_recommendations WHERE user_id = ?", user[0]["id"])
        else:
            flash("User not found")
            return redirect(url_for("dashboard"))

        for project in projects:
            project["start_date"] = datetime.strptime(project["start_date"], "%Y-%m-%d").strftime("%B %d, %Y") if project["start_date"] else None
            project["end_date"] = datetime.strptime(project["end_date"], "%Y-%m-%d").strftime("%B %d, %Y") if project["end_date"] else "ongoing"
    else:
        flash("The Name you searched for does not exist")
        return redirect(url_for("dashboard"))

    person = {
        "query": query,
        "user": user,
        "books": books,
        "projects": projects,
        "hobbies": hobbies,
        "possessions": possessions,
        "networth": networth,
        "jobs": jobs,
        "book_recommendations": book_recommendations,
    }
    return render_template("search.html", person=person)

@app.route("/user_profile/<int:user_id>")
@login_required
def user_profile(user_id):
    """Display user profile"""
    user_profile_image = "/static/uploads/default.jpg"
    # Simulate fetching the user's profile image from a database
    # In a real application, you would fetch this from the database
    # user_profile_image = db.execute("SELECT profile_image FROM users WHERE id = ?", user_id)
    # For now, let's assume it updates a variable
    # user_profile_image = user_profile_image[0]['profile_image'] if user_profile_image else "/static/uploads/default.jpg"
    # Fetch user data from the database
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    if not user:
        flash("User not found")
        return redirect(url_for("search"))
    jobs = db.execute("SELECT * FROM jobs WHERE user_id = ?", user_id)
    projects = db.execute("SELECT * FROM projects WHERE user_id = ?", user_id)
    book_recommendations = db.execute("SELECT * FROM book_recommendations WHERE user_id = ?", user_id)
    networth = db.execute("SELECT * FROM networth WHERE user_id = ?", user_id)

    profile = {
        "user": user[0],
        "projects": projects,
        "jobs": jobs,
        "book_recommendations": book_recommendations,
        "networth": networth[0] if networth else None,
    }

    return render_template("user_profile.html", profile=profile, profile_image=user_profile_image)

# Helper function to check file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to handle profile image upload
@app.route('/upload', methods=['POST'])
@login_required
def upload_profile():
    if 'profile_pic' not in request.files:
        flash('No file part')
        return redirect(request.referrer)

    file = request.files['profile_pic']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.referrer)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Here, you should update the user's profile picture path in the database
        # For now, let's assume it updates a variable
        db.execute("UPDATE users SET profile_image = ? WHERE id = ?", file_path, request.form.get('user_id'))
        flash('Profile picture uploaded spremieruccessfully!')

        return redirect(url_for('user_profile', user_id=request.form.get('user_id')))

    flash('Invalid file type. Allowed types: png, jpg, jpeg, gif')
    return redirect(request.referrer)

@app.route("/books_catalog", methods=["GET", "POST"])
@login_required
def books_catalog():
    """Manage book catalog"""
    if request.method == "POST":
        user_id = request.form.get("user_id")
        book_id = request.form.get("book_id")
        action_type = request.form.get("action_type")
        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        date_read = request.form.get("date_read")
        if action_type == "update":
            if not book_id:
                flash("No book ID provided")
                return redirect(url_for("books_catalog", user_id=user_id))

            fields = []
            values = []

            if title:
                fields.append("title =?")
                values.append(title)
            if author:
                fields.append("author =?")
                values.append(author)
            if date_read:
                fields.append("date_read =?")
                values.append(date_read)
            if genre:
                fields.append("genre =?")
                values.append(genre)

            if fields:
                query = f"UPDATE books_read SET {', '.join(fields)} WHERE id =?"
                values.extend(book_id)
                db.execute(query, *values)
                flash("Book updated successfully")
                return redirect(url_for("books_catalog", user_id=user_id))
            else:
                flash("No fields provided for update")
        elif action_type == "insert":
            if not title or not author or not date_read:
                flash("Provide all book information")
                return redirect(url_for("books_catalog", user_id=user_id))
            db.execute("INSERT INTO books_read (user_id, title, author, date_read, genre) VALUES(?,?,?,?,?)", user_id, title, author, date_read, genre)
            flash("Book added successfully")
            return redirect(url_for("books_catalog", user_id=user_id))
        elif action_type == "delete":
            if not book_id:
                flash("No book ID provided")
                return redirect(url_for("books_catalog", user_id=user_id))
            db.execute("DELETE FROM books_read WHERE id = ?", book_id)
            flash("Book deleted successfully")
            return redirect(url_for("books_catalog", user_id=user_id))
        else:
            flash("Invalid action type")
            return redirect(url_for("books_catalog", user_id=user_id))
    user_id = request.args.get("user_id")
    books = db.execute("SELECT * FROM books_read WHERE user_id =?", user_id)
    return render_template("books_catalog.html", books=books, user_id=user_id)

@app.route("/edit_projects", methods=["GET", "POST"])
@login_required
def edit_projects():
    """Manage projects"""
    if request.method == "POST":
        user_id = request.form.get("user_id")
        action_type = request.form.get("action_type")
        title = request.form.get("title")
        description = request.form.get("description")
        github_link = request.form.get("github_link")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        project_id = request.form.get("project_id")
        if action_type == "update":
            if not project_id:
                flash("No project ID provided")
                return redirect(url_for("edit_projects", user_id=user_id))

            fields = []
            values = []

            if title:
                fields.append("title =?")
                values.append(title)
            if description:
                fields.append("description =?")
                values.append(description)
            if github_link:
                fields.append("github_link =?")
                values.append(github_link)
            if start_date:
                fields.append("start_date =?")
                values.append(start_date)
            if end_date:
                fields.append("end_date =?")
                values.append(end_date)
                fields.append("start_date =?")
                values.append(start_date)

            if fields:
                query = f"UPDATE projects SET {', '.join(fields)} WHERE id =?"
                values.extend(project_id)
                db.execute(query, *values)
                flash("Project updated successfully")
                return redirect(url_for("edit_projects", user_id=user_id))
            else:
                flash("No fields provided for update")
        elif action_type == "insert":
            if not title or not description or not github_link or not start_date or not end_date:
                flash("Provide all project information")
                return redirect(url_for("edit_projects", user_id=user_id))
            db.execute("INSERT INTO projects (user_id, title, description, github_link, start_date, end_date) VALUES(?,?,?,?,?,?)", user_id, title, description, github_link, start_date, end_date)
            flash("Project added successfully")
            return redirect(url_for("edit_projects", user_id=user_id))
        elif action_type == "delete":
            if not project_id:
                flash("No project ID provided")
                return redirect(url_for("edit_projects", user_id=user_id))
            db.execute("DELETE FROM projects WHERE id = ?", project_id)
            flash("Project deleted successfully")
            return redirect(url_for("edit_projects", user_id=user_id))
        else:
            flash("Invalid action type")
            return redirect(url_for("edit_projects", user_id=user_id))

    user_id = request.args.get("user_id")
    projects = db.execute("SELECT * FROM projects WHERE user_id =?", user_id)
    return render_template("edit_projects.html", projects=projects, user_id=user_id)

@app.route("/editpossessions", methods=["GET", "POST"])
@login_required
def edit_possessions():
    """Manage possessions"""
    if request.method == "POST":
        user_id = request.form.get("user_id")
        action_type = request.form.get("action_type")
        item_name = request.form.get("item_name")
        category = request.form.get("category")
        value = request.form.get("value")
        possession_id = request.form.get("possession_id")
        if action_type == "update":
            if not possession_id:
                flash("No possession ID provided")
                return redirect(url_for("edit_possessions", user_id=user_id))

            fields = []
            values = []

            if item_name:
                fields.append("item_name =?")
                values.append(item_name)
            if category:
                fields.append("category =?")
                values.append(category)
            if value:
                fields.append("value =?")
                values.append(value)

            if fields:
                query = f"UPDATE possessions SET {', '.join(fields)} WHERE id =?"
                values.extend(possession_id)
                db.execute(query, *values)
                flash("Possession updated successfully")
                return redirect(url_for("edit_possessions", user_id=user_id))
            else:
                flash("No fields provided for update")
        elif action_type == "insert":
            if not item_name or not category or not value:
                flash("Provide all possession information")
                return redirect(url_for("edit_possessions", user_id=user_id))
            db.execute("INSERT INTO possessions (user_id, item_name, category, value) VALUES(?,?,?,?)", user_id, item_name, category, value)
            flash("Possession added successfully")
            return redirect(url_for("edit_possessions", user_id=user_id))
        elif action_type == "delete":
            if not possession_id:
                flash("No possession ID provided")
                return redirect(url_for("edit_possessions", user_id=user_id))
            db.execute("DELETE FROM possessions WHERE id = ?", possession_id)
            flash("Possession deleted successfully")
            return redirect(url_for("edit_possessions", user_id=user_id))
        else:
            flash("Invalid action type")
            return redirect(url_for("edit_possessions", user_id=user_id))

    user_id = request.args.get("user_id")
    possessions = db.execute("SELECT * FROM possessions WHERE user_id =?", user_id)
    return render_template("edit_possessions.html", possessions=possessions, user_id=user_id)

@app.route("/edit_jobs", methods=["GET", "POST"])
@login_required
def edit_jobs():
    """Manage jobs"""
    if request.method == "POST":
        user_id = request.form.get("user_id")
        action_type = request.form.get("action_type")
        job_id = request.form.get("job_id")
        title = request.form.get("title")
        company = request.form.get("company")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        description = request.form.get("description")
        if action_type == "update":
            if not job_id:
                flash("No job ID provided")
                return redirect(url_for("edit_jobs", user_id=user_id))

            fields = []
            values = []

            if title:
                fields.append("title =?")
                values.append(title)
            if company:
                fields.append("company =?")
                values.append(company)
            if start_date:
                fields.append("start_date =?")
                values.append(start_date)
            if end_date:
                fields.append("end_date =?")
                values.append(end_date)
            if description:
                fields.append("description =?")
                values.append(description)

            if fields:
                query = f"UPDATE jobs SET {', '.join(fields)} WHERE id =?"
                values.extend(job_id)
                db.execute(query, *values)
                flash("Job updated successfully")
                return redirect(url_for("edit_jobs", user_id=user_id))
            else:
                flash("No fields provided for update")
        elif action_type == "insert":
            if not title or not company or not start_date or not end_date or not description:
                flash("Provide all job information")
                return redirect(url_for("edit_jobs", user_id=user_id))
            db.execute("INSERT INTO jobs (user_id, title, company, start_date, end_date, description) VALUES(?,?,?,?,?,?)", user_id, title, company, start_date, end_date, description)
            flash("Job added successfully")
            return redirect(url_for("edit_jobs", user_id=user_id))
        elif action_type == "delete":
            if not job_id:
                flash("No job ID provided")
                return redirect(url_for("edit_jobs", user_id=user_id))
            db.execute("DELETE FROM jobs WHERE id = ?", job_id)
            flash("Job deleted successfully")
            return redirect(url_for("edit_jobs", user_id=user_id))
        else:
            flash("Invalid action type")
            return redirect(url_for("edit_jobs", user_id=user_id))
    user_id = request.args.get("user_id")
    jobs = db.execute("SELECT * FROM jobs WHERE user_id =?", user_id)
    return render_template("edit_jobs.html", jobs=jobs, user_id=user_id)


@app.route("/edit_networth", methods=["GET", "POST"])
@login_required
def edit_networth():
    """Manage net worth"""
    if request.method == "POST":
        user_id = request.form.get("user_id")
        networth_id = request.form.get("networth_id")
        action_type = request.form.get("action_type")
        total_value = request.form.get("total_value")
        date_recorded = request.form.get("date_recorded")
        networth_id = request.form.get("networth_id")
        if action_type == "update":
            if not networth_id:
                flash("No net worth ID provided")
                return redirect(url_for("edit_networth", user_id=user_id))

            fields = []
            values = []

            if total_value:
                fields.append("total_value =?")
                values.append(total_value)
            if date_recorded:
                fields.append("date_recorded =?")
                values.append(date_recorded)

            if fields:
                query = f"UPDATE networth SET {', '.join(fields)} WHERE id =?"
                values.extend(networth_id)
                db.execute(query, *values)
                flash("Net worth updated successfully")
                return redirect(url_for("edit_networth", user_id=user_id))
            else:
                flash("No fields provided for update")
        elif action_type == "insert":
            if not total_value or not date_recorded:
                flash("Provide all net worth information")
                return redirect(url_for("edit_networth", user_id=user_id))
            db.execute("INSERT INTO networth (user_id, total_value, date_recorded) VALUES(?,?,?)", user_id, total_value, date_recorded)
            flash("Net worth added successfully")
            return redirect(url_for("edit_networth", user_id=user_id))
        elif action_type == "delete":
            if not networth_id:
                flash("No net worth ID provided")
                return redirect(url_for("edit_networth", user_id=user_id))
            db.execute("DELETE FROM networth WHERE id = ?", networth_id)
            flash("Net worth deleted successfully")
            return redirect(url_for("edit_networth", user_id=user_id))
        else:
            flash("Invalid action type")
            return redirect(url_for("edit_networth", user_id=user_id))
    user_id = request.args.get("user_id")
    networth = db.execute("SELECT * FROM networth WHERE user_id =?", user_id)
    return render_template("edit_networth.html", networth=networth, user_id=user_id)

@app.route("/edit_book_recommendations", methods=["GET", "POST"])
@login_required
def edit_book_recommendations():
    """Manage book recommendations"""
    if request.method == "POST":
        user_id = request.form.get("user_id")
        action_type = request.form.get("action_type")
        book_id = request.form.get("book_id")
        book_title = request.form.get("book_title")
        author = request.form.get("author")
        reason = request.form.get("reason")
        if action_type == "update":
            if not book_id:
                flash("No book ID provided")
                return redirect(url_for("edit_book_recommendations", user_id=user_id))

            fields = []
            values = []

            if book_title:
                fields.append("book_title =?")
                values.append(book_title)
            if author:
                fields.append("author =?")
                values.append(author)
            if reason:
                fields.append("reason =?")
                values.append(reason)

            if fields:
                query = f"UPDATE book_recommendations SET {', '.join(fields)} WHERE id =?"
                values.extend(book_id)
                db.execute(query, *values)
                flash("Book recommendation updated successfully")
                return redirect(url_for("edit_book_recommendations", user_id=user_id))
            else:
                flash("No fields provided for update")
        elif action_type == "insert":
            if not book_title or not author or not reason:
                flash("Provide all book recommendation information")
                return redirect(url_for("edit_book_recommendations", user_id=user_id))
            db.execute("INSERT INTO book_recommendations (user_id, book_title, author, reason) VALUES(?,?,?,?)", user_id, book_title, author, reason)
            flash("Book recommendation added successfully")
            return redirect(url_for("edit_book_recommendations", user_id=user_id))
        elif action_type == "delete":
            if not book_id:
                flash("No book ID provided")
                return redirect(url_for("edit_book_recommendations", user_id=user_id))
            db.execute("DELETE FROM book_recommendations WHERE id = ?", book_id)
            flash("Book recommendation deleted successfully")
            return redirect(url_for("edit_book_recommendations", user_id=user_id))
        else:
            flash("Invalid action type")
            return redirect(url_for("edit_book_recommendations", user_id=user_id))

    user_id = request.args.get("user_id")
    book_recommendations = db.execute("SELECT * FROM book_recommendations WHERE user_id =?", user_id)
    return render_template("edit_book_recommendations.html", book_recommendations=book_recommendations, user_id=user_id)

@app.route("/edit_hobbies", methods=["GET", "POST"])
@login_required
def edit_hobbies():
    """Manage hobbies"""
    if request.method == "POST":
        user_id = request.form.get("user_id")
        action_type = request.form.get("action_type")
        hobby_id = request.form.get("hobby_id")
        hobby = request.form.get("hobby")
        
        if action_type == "update":
            if not hobby_id:
                flash("No hobby ID provided")
                return redirect(url_for("edit_hobbies", user_id=user_id))

            fields = []
            values = []

            if hobby:
                fields.append("hobby =?")
                values.append(hobby)

            if fields:
                query = f"UPDATE hobbies SET {', '.join(fields)} WHERE id =?"
                values.extend(hobby_id)
                db.execute(query, *values)
                flash("Hobby updated successfully")
                return redirect(url_for("edit_hobbies", user_id=user_id))
            else:
                flash("No fields provided for update")
        elif action_type == "insert":
            if not hobby:
                flash("Provide all hobby information")
                return redirect(url_for("edit_hobbies", user_id=user_id))
            db.execute("INSERT INTO hobbies (user_id, hobby) VALUES(?,?)", user_id, hobby)
            flash("Hobby added successfully")
            return redirect(url_for("edit_hobbies", user_id=user_id))
        elif action_type == "delete":
            if not hobby_id:
                flash("No hobby ID provided")
                return redirect(url_for("edit_hobbies", user_id=user_id))
            db.execute("DELETE FROM hobbies WHERE id = ?", hobby_id)
            flash("Hobby deleted successfully")
            return redirect(url_for("edit_hobbies", user_id=user_id))
        else:
            flash("Invalid action type")
            return redirect(url_for("edit_hobbies", user_id=user_id))
    user_id = request.args.get("user_id")
    hobbies = db.execute("SELECT * FROM hobbies WHERE user_id =?", user_id)
    if not hobbies:
        flash("No hobbies found for this user")
        return redirect(url_for("search"))
    return render_template("edit_hobbies.html", hobbies=hobbies, user_id=user_id)

@app.route("/helper")
@login_required
def helper():
    query = request.args.get("q")
    if not query:
        return ""

    # Search for users whose usernames start with or contain the query
    users = db.execute("SELECT username FROM users WHERE username LIKE ?", f"%{query}%")

    # Return HTML list items for each matching user
    return render_template("user_list.html", users=users)
