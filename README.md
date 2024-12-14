# Advertisement Board Web Application

## Description

The Advertisement Board Web Application is a platform where users can create, manage, and interact with advertisements. Users can register, log in, and perform actions such as adding, editing, completing, deleting, and permanently deleting advertisements. The application also allows users to like or dislike advertisements created by others.

## Features

* User Authentication: Sign up, log in, and log out functionality.

* Create Advertisements: Users can create advertisements with up to 4 photos.

* Manage Advertisements:

  * Edit advertisements if the user is the author.
  
  * Mark advertisements as completed.
  
  * Delete advertisements temporarily or permanently.
  
  * Activate previously completed or deleted advertisements.

* Advertisement Interaction:

  * View advertisements in a paginated list.
  
  * Like or dislike advertisements.

* User Dashboard:

  * View all advertisements created by the logged-in user.
  
  * Filter advertisements by active, completed, or deleted status.
  
  * Paginated view for user advertisements.

## Technologies Used

* Backend: Django (Python)

* Frontend: HTML, CSS

* Database: SQLite (default Django database backend)

## Prerequisites

* Python 3.8+

* Django 3.2+

## Installation

1. Clone the Repository

git clone https://github.com/your-repository-url/advertisement-board.git
cd advertisement-board

2. Create a Virtual Environment

```python
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install Dependencies

```python
pip install -r requirements.txt
```

4. Run Migrations

```python
python manage.py migrate
```

5. Create a Superuser (for admin access)

```python
python manage.py createsuperuser
```

6. Run the Development Server

```python
python manage.py runserver
```

7. Access the Application
Open your web browser and navigate to

```python
http://127.0.0.1:8000.
```

## Usage

### User Authentication

* Navigate to /signup/ to create a new account.

* Log in using your credentials at /login/.

### Advertisements

1. After logging in, navigate to /board/ to view all active advertisements.

2. Click "Add" to create a new advertisement. Upload photos and fill in the details.

3. Use the menu button (three dots) next to your advertisements to:

* Edit the advertisement

* Mark it as completed

* Delete it

4. Reactivate completed or deleted advertisements by navigating to the appropriate tab in your dashboard.

### Voting

* Click the thumbs-up or thumbs-down icons on an advertisement to like or dislike it.

## Project Structure

```
WebApp/
|-- AdvBoard/                   # Main application folder
|   |-- migrations/          # Database migration files
|   |-- templates/board/     # HTML templates for the board app
|   |-- views.py             # View functions
|   |-- forms.py             # Database forms
|   |-- models.py            # Database models
|   |-- urls.py              # URL routing for the board app
|-- static/                  # Static files (CSS, JavaScript, Images)
|-- templates/               # Base templates
|-- manage.py                # Django management script
|-- requirements.txt         # List of dependencies
```

### Key Files

* models.py: Defines the Advertisement model with fields for title, content, photos, and user interactions.

* views.py: Contains all the view logic for handling user requests.

* urls.py: Defines routes for the application.

* templates/: Contains the HTML templates used for rendering pages.

### API Endpoints

#### Advertisement Endpoints

* GET /board/: View all active advertisements (paginated).

* GET /board/<pk>/: View details of a specific advertisement.

* POST /board/add/: Add a new advertisement.

* POST /board/edit/<pk>/: Edit an existing advertisement.

* POST /board/complete/<pk>/: Mark an advertisement as completed.

* POST /board/delete/<pk>/: Delete an advertisement.

* POST /board/delete-completely/<pk>/: Permanently delete an advertisement.

* POST /board/activate/<pk>/: Reactivate a completed or deleted advertisement.

#### Voting Endpoints

* POST /board/<pk>/like/: Like an advertisement.

* POST /board/<pk>/dislike/: Dislike an advertisement.

## Screenshots

### Login page:
![login](https://github.com/asstrix/files/blob/main/AdvBoard/login.png?raw=true)

### Sign up page:
![signup](https://github.com/asstrix/files/blob/main/AdvBoard/signup.png?raw=true)

### Board page:
![board](https://github.com/asstrix/files/blob/main/AdvBoard/board.png?raw=true)

### My advertisements page:
![myads](https://github.com/asstrix/files/blob/main/AdvBoard/myads.png?raw=true)

### Edit advertisement page:
![editadd](https://github.com/asstrix/files/blob/main/AdvBoard/editadd.png?raw=true)

## Future Enhancements

* Add user profiles with avatars.

* Add a search and filtering system for advertisements.

* Enable image preview during advertisement creation and editing.

* Support for email notifications for actions such as advertisement completion or deletion.

* Add comments for addvertisements.
