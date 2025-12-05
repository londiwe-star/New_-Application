# News Portal - Django News Application

A comprehensive Django-based news portal application with role-based access control, subscription management, email notifications, and Twitter/X integration.

## Features

- **Custom User Model** with three roles: Reader, Editor, and Journalist
- **Publisher Management** with editor and journalist associations
- **Article Management** with approval workflow
- **Newsletter System** for periodic content distribution
- **Subscription System** for readers to follow publishers and journalists
- **Email Notifications** when articles are approved
- **Twitter/X Integration** for automatic posting of approved articles
- **RESTful API** with authentication and pagination
- **Responsive Bootstrap 5 UI** for all views
- **Comprehensive Admin Interface** with customizations
- **Unit and Integration Tests** for all components

## Project Structure

```
news_portal/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── news_portal/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── news/
    ├── models.py
    ├── views.py
    ├── api_views.py
    ├── serializers.py
    ├── urls.py
    ├── api_urls.py
    ├── forms.py
    ├── signals.py
    ├── admin.py
    ├── tests.py
    ├── management/
    │   └── commands/
    │       ├── setup_groups.py
    │       └── create_sample_data.py
    ├── templates/
    │   ├── base.html
    │   ├── home.html
    │   ├── article_list.html
    │   ├── article_detail.html
    │   └── registration/
    └── static/
        ├── css/
        └── js/
```

## Installation

### Prerequisites

- Python 3.8 or higher
- MariaDB/MySQL database server
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd News_app
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Database Setup

1. Create a MariaDB database:

```sql
CREATE DATABASE news_portal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'your_db_user'@'localhost' IDENTIFIED BY 'your_db_password';
GRANT ALL PRIVILEGES ON news_portal_db.* TO 'your_db_user'@'localhost';
FLUSH PRIVILEGES;
```

2. Install MySQL client libraries:

```bash
# On Ubuntu/Debian
sudo apt-get install default-libmysqlclient-dev

# On Windows (using conda)
conda install mysqlclient

# Or use pip (may require Visual C++ Build Tools on Windows)
pip install mysqlclient
```

### Step 5: Environment Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit `.env` and configure the following:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database Configuration
DB_NAME=news_portal_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# Email Configuration (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Twitter/X API Configuration
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
TWITTER_ACCESS_TOKEN=your-twitter-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-twitter-access-token-secret
TWITTER_BEARER_TOKEN=your-twitter-bearer-token
```

**Note:** For Gmail, you'll need to generate an App Password:
1. Go to Google Account settings
2. Security → 2-Step Verification → App passwords
3. Generate a password for "Mail"

### Step 6: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Set Up Groups and Permissions

```bash
python manage.py setup_groups
```

This command creates three groups (READERs, EDITORs, JOURNALISTs) and assigns appropriate permissions.

### Step 8: Create Sample Data (Optional)

```bash
python manage.py create_sample_data
```

This creates sample users, publishers, articles, and newsletters for testing.

### Step 9: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 10: Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

## User Roles

### Reader
- View approved articles and newsletters
- Subscribe to publishers and journalists
- Access personalized dashboard with subscribed content

### Journalist
- Create and edit articles
- Create newsletters
- View own articles and statistics
- Publish independently or through publishers

### Editor
- Approve/reject articles
- View all articles (approved and pending)
- Manage content quality

## API Documentation

### Authentication

The API uses Token Authentication. Get your token:

```bash
POST /api/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

Response:
```json
{
    "token": "your_auth_token"
}
```

Use the token in subsequent requests:

```bash
Authorization: Token your_auth_token
```

### Endpoints

#### Get Subscribed Articles
```http
GET /api/articles/subscribed/
Authorization: Token your_auth_token
```

Returns paginated list of articles from user's subscribed publishers and journalists.

#### Get Publisher Articles
```http
GET /api/articles/publisher/{publisher_id}/
Authorization: Token your_auth_token
```

Returns paginated list of approved articles from a specific publisher.

#### Get Journalist Articles
```http
GET /api/articles/journalist/{journalist_id}/
Authorization: Token your_auth_token
```

Returns paginated list of approved articles from a specific journalist.

#### List Publishers
```http
GET /api/publishers/
Authorization: Token your_auth_token
```

Returns list of all publishers.

### Pagination

All article endpoints support pagination:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

Example:
```http
GET /api/articles/subscribed/?page=2&page_size=10
```

## Running Tests

Run all tests:

```bash
python manage.py test
```

Run specific test classes:

```bash
python manage.py test news.tests.UserModelTests
python manage.py test news.tests.APITests
```

Run with coverage:

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Deployment

### Production Settings

1. Set `DEBUG=False` in `.env`
2. Set a strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS` in settings.py
4. Use a production WSGI server (e.g., Gunicorn)
5. Set up a reverse proxy (e.g., Nginx)
6. Use a production database
7. Configure static files serving
8. Set up SSL/HTTPS

### Example Gunicorn Configuration

```bash
pip install gunicorn
gunicorn news_portal.wsgi:application --bind 0.0.0.0:8000
```

### Static Files

```bash
python manage.py collectstatic
```

## Management Commands

### setup_groups

Creates groups and assigns permissions:

```bash
python manage.py setup_groups
```

### create_sample_data

Creates sample data for development:

```bash
python manage.py create_sample_data
```

## Email Configuration

The application sends email notifications when articles are approved. Configure email settings in `.env`:

- **Gmail SMTP**: Use App Password (not regular password)
- **Other Providers**: Adjust `EMAIL_HOST` and `EMAIL_PORT` accordingly

## Twitter/X Integration

To enable Twitter/X posting:

1. Create a Twitter Developer account
2. Create an app and get API credentials
3. Add credentials to `.env`
4. The application will automatically post when articles are approved

**Note:** Twitter API v2 requires Bearer Token or OAuth 1.0a. The current implementation supports Bearer Token. For OAuth 1.0a, you may need to install `requests-oauthlib`.

## Security Features

- CSRF protection enabled
- Secure password hashing (Django's default PBKDF2)
- SQL injection prevention (Django ORM)
- XSS protection (Django's auto-escaping)
- Permission-based access control
- Token-based API authentication

## Troubleshooting

### Database Connection Issues

- Verify MariaDB is running
- Check database credentials in `.env`
- Ensure database exists and user has permissions
- Check firewall settings

### Email Not Sending

- Verify email credentials in `.env`
- For Gmail, ensure App Password is used (not regular password)
- Check spam folder
- Verify `EMAIL_BACKEND` in settings

### Twitter Posting Not Working

- Verify API credentials in `.env`
- Check Twitter API rate limits
- Review logs for error messages
- Ensure Bearer Token has write permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the documentation
- Review the test files for usage examples
- Open an issue on GitHub

## Acknowledgments

- Django Framework
- Django REST Framework
- Bootstrap 5
- Bootstrap Icons

---

**Built with Django 4.2+**


