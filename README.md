# Project Title: Inspire

### 📹 Video Demo:
[https://youtu.be/T6JldDczqqM]

---

## ✨ Description

**Inspire** is a web-based platform designed to uplift users by allowing them to explore the journeys of others. Users can view books read, projects completed, possessions acquired, jobs held, net worth, hobbies, and book recommendations of others on the platform. The goal is to provide real-life inspiration through the shared experiences of other users.

Once a user logs in through the login page, they are taken to the dashboard where they can search for their "icons"—other users they look up to. By typing a name or part of a name into the search bar, matching users from the database appear below the input field. When a user selects and searches for an icon, they are taken to a profile view displaying all the inspirational content shared by that individual. They can also view a brief professional summary of the user through the portfolio section.

---

## 🔧 Technologies Used

- **Python (Flask Framework)** – Handles routing and backend logic
- **SQLite3** – Lightweight embedded database
- **Jinja2** – Templating engine for dynamic HTML rendering
- **HTML/CSS/Bootstrap** – Frontend layout and responsiveness
- **JavaScript** – Adds interactivity (e.g., dynamic search)
- **Render.com** – Deployment platform for hosting the application

---

## 📁 Project Structure & File Descriptions

This project follows the **MVC (Model-View-Controller)** architecture pattern.

### 🧠 Model

- **`inspire.db`**  
  The SQLite3 database file that stores user information, including authentication data and user-generated content such as books, projects, possessions, jobs, hobbies, and more.

---

### 🎮 Controller

- **`app.py`**  
  Acts as the main controller of the application. It defines the backend logic and routes, handles user registration, login/logout, search functionality, CRUD operations for user content, and serves appropriate templates.

---

### 🎨 Views (`/templates` folder)

Contains all HTML templates rendered using Flask and Jinja2.

- **`landingpage.html`**  
  Public-facing homepage introducing the Inspire platform.

- **`index.html`**  
  Dashboard displayed post-login. Allows users to search for their icons.

- **`login.html`**  
  Enables returning users to log in.

- **`register.html`**  
  New users can register to create an account.

- **`search.html`**  
  Displays all details of a searched user, organized under various tabs (books, projects, net worth, jobs, hobbies, possessions, and recommendations).

- **`user_profile.html`**  
  Shows a brief biography or summary of the selected user.

- **`user_list.html`**  
  Provides live search suggestions as the user types in the search bar.

---

### ✏️ Editable Templates (User-only access)

These templates allow users to manage their own data (Create, Read, Update, Delete).

- `books_catalog.html`  
- `edit_book_recommendations.html`  
- `edit_projects.html`  
- `edit_possessions.html`  
- `edit_jobs.html`  
- `edit_networth.html`  
- `edit_hobbies.html`  

Each template lets a user manage their specific content area privately and securely.

---

## 🖼️ Static Files (`/static` folder)

- **`style.css`**  
  Custom styles to enhance the look and feel of the app beyond what Bootstrap offers.

- **`/uploads/`**  
  Stores user-uploaded images such as profile photos.

- **Image Assets**  
  Used across pages to add visual flair (e.g., background images, dashboard graphics).

---

## 🔍 Search Functionality

Users can search for other users (icons) via the dashboard. The platform implements an autocomplete-style live search feature using a helper Flask route and JavaScript. As a user types into the search box, matching usernames from the database appear. Upon selection and search, the app displays the full profile of that user.

---

## 🧪 Requirements

All required dependencies are listed in the `requirements.txt` file.

To generate the file (after installing packages locally), run:
```bash
pip freeze > requirements.txt

## 🚀 Deployment

The application is deployed on **Render.com**, and can be accessed live here: [Live Demo of Inspire](https://inspire-app-cznh.onrender.com/), allowing users to interact with Inspire from anywhere with an internet connection. The deployment includes the Flask backend, templates, and static content. Render ensures automatic redeployment upon each GitHub push.


---

## ✅ Future Enhancements

- Add messaging functionality between users  
- Enable followers or mentorship-style connections  
- Add tags/categories for icons (e.g., "tech", "education", "finance")  
- Social media integration for sharing inspiring profiles  
- Enhanced analytics dashboard for user activity  

---

## 💡 Reflections

Creating **Inspire** was both a technical and personal journey. It challenged me to blend full-stack development skills into a meaningful product—something that doesn't just function, but **matters**. One of the most important lessons was balancing usability with privacy and ensuring that each user controls their narrative on the platform.

Design-wise, decisions such as organizing content into tabs under user profiles and enforcing CRUD access control were made to prioritize clarity, security, and a smooth user experience. I also made intentional use of the **MVC structure** for maintainability and scalability.

Through **Inspire**, I hope to create a platform where people grow by sharing and learning from each other—where ordinary stories spark extraordinary ideas.

---

## 📝 Conclusion

**Inspire** transforms personal storytelling into a tool for collective empowerment. Whether you’re seeking motivation, admiring a peer’s journey, or reflecting on your own path, Inspire provides the digital space to do it meaningfully.
