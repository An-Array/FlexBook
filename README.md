![FlexBook](https://socialify.git.ci/An-Array/FlexBook/image?font=Source+Code+Pro&language=1&name=1&owner=1&pattern=Brick+Wall&theme=Dark)
# FlexBook 📅

FlexBook is a modern backend API for a resource booking platform that allows users to book various resources such as meeting rooms, event spaces, and co-working desks. Built with FastAPI, it's designed for scalability and reliability.

## 📖 About the Project

This project provides the backend services for the FlexBook platform. It handles user authentication, venue management, and booking logic. The API is designed to be RESTful and provides a clear and consistent interface for client applications.

## 🌐 Live Demo

- **🎯 Frontend Application**: [https://flexbook-on.streamlit.app/](https://flexbook-on.streamlit.app/)
- **📖 API Documentation**: [https://flexbook-backend.onrender.com/docs](https://flexbook-backend.onrender.com/docs)
- **📋 Alternative API Docs**: [https://flexbook-backend.onrender.com/redoc](https://flexbook-backend.onrender.com/redoc)

## ✨ Features

### User Management
- **Authentication**: Secure user registration and login with JWT authentication
- **Role-Based Access Control (RBAC)**: Three distinct roles - `user`, `owner`, and `admin`
- **Self-Service**: Users can update and delete their own accounts
- **Administrative Control**: Admins have full user management capabilities

### Venue Management
- **Content Management**: `owner` and `admin` roles can create, update, and delete venues
- **Public Access**: All users can browse venues and view detailed information
- **Flexible Resource Types**: Supports meeting rooms, event spaces, co-working desks, and more

### Booking Management
- **Authenticated Bookings**: Secure booking system for registered users
- **Conflict Prevention**: Intelligent system prevents double-bookings for the same venue and time slot
- **User Control**: Users can view, update, and cancel their own bookings
- **Admin Oversight**: Full administrative access to all bookings for management purposes

## 🛠️ Technology Stack

### Frontend
- **[Streamlit](https://streamlit.io/)**: Interactive web application framework for Python
- **Live Frontend**: [flexbook-on.streamlit.app](https://flexbook-on.streamlit.app/)
- **Frontend Repository**: [github.com/An-Array/FlexBook--frontend](https://github.com/An-Array/FlexBook--frontend)

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)**: High-performance web framework with automatic API documentation
- **[SQLAlchemy](https://www.sqlalchemy.org/)**: Powerful ORM for database operations
- **[Alembic](https://alembic.sqlalchemy.org/)**: Database migration management
- **[Pydantic](https://pydantic-docs.helpmanual.io/)**: Data validation and serialization
- **[PostgreSQL](https://www.postgresql.org/)**: Robust relational database system
- **[CORSMiddleware](https://fastapi.tiangolo.com/tutorial/cors/)**: FastAPI middleware that allows the frontend application to make requests

### Testing & Quality Assurance
- **[Pytest](https://docs.pytest.org/)**: Comprehensive testing framework
- **[Locust](https://locust.io/)**: Load testing and performance validation

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- PostgreSQL
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/An-Array/FlexBook.git
   cd FlexBook
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Configure environment**
   
   Create a `.env` file in the root directory:
   ```env
   database_hostname=localhost
   database_port=5432
   database_password=your_database_password
   database_name=your_database_name
   database_username=your_database_username
   secret_key=your_secret_key
   algorithm=HS256
   access_token_expire_minutes=60
   panel_key=your_panel_key
   front_url=http://localhost:3000  # Frontend URL for CORS configuration
   ```
   
   **Note**: The `front_url` variable configures CORS middleware to allow requests from your frontend application. Update this to match your frontend's deployment URL in production.

5. **Initialize database**
   ```bash
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be accessible at `http://127.0.0.1:8000`.

## 🌐 CORS Configuration

FlexBook uses **CORSMiddleware** from `fastapi.middleware.cors` to enable cross-origin requests between the frontend and backend applications.

### How CORS is Implemented
- **Middleware**: `CORSMiddleware` is added to the FastAPI application
- **Origin Control**: The `front_url` environment variable specifies which frontend origins are allowed to make requests
- **Security**: Prevents unauthorized cross-origin requests while allowing legitimate frontend communication
- **Development vs Production**: Different `front_url` values for local development (`http://localhost:3000`) and production (`https://flexbook-on.streamlit.app`)

### Configuration
The CORS settings are controlled through the `front_url` environment variable:
```python
# Example CORS configuration in FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[front_url],  # Configured via environment variable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🔬 Testing

### Unit & Integration Tests
To run the test suite, use the following command:
```bash
pytest
```

### Load Testing
First, ensure the application is running, then:
```bash
locust -f tests/race_condition.py --host http://127.0.0.1:8000
```

## 🗄️ Database Management

### Create Migration
```bash
alembic revision --autogenerate -m "Migration description"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1
```

## 📚 API Documentation

### Live Documentation
- **🌍 Production API**: [https://flexbook-backend.onrender.com/docs](https://flexbook-backend.onrender.com/docs)
- **📋 ReDoc Format**: [https://flexbook-backend.onrender.com/redoc](https://flexbook-backend.onrender.com/redoc)

### Local Development
Once your local application is running:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### Core Endpoints

#### Authentication & Users
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `POST` | `/signup` | Create new user account | Public |
| `POST` | `/login` | User authentication | Public |
| `GET` | `/users` | List all users | Admin only |
| `GET` | `/users/{id}` | Get user details | Owner/Admin |
| `PUT` | `/users/{id}` | Update user information | Owner/Admin |
| `DELETE` | `/users/{id}` | Delete user account | Owner/Admin |
| `PUT` | `/panel` | Update user role | Admin only |

#### Venues
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `POST` | `/venues` | Create new venue | Owner/Admin |
| `GET` | `/venues` | List all venues | All users |
| `GET` | `/venues/{id}` | Get venue details | All users |
| `PUT` | `/venues/{id}` | Update venue | Owner/Admin |
| `DELETE` | `/venues/{id}` | Delete venue | Owner/Admin |

#### Bookings
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `POST` | `/bookings` | Create booking | Authenticated |
| `GET` | `/bookings` | List all bookings | Admin only |
| `GET` | `/bookings/{id}` | Get booking details | Owner/Admin |
| `PUT` | `/bookings/{id}` | Update booking | Owner/Admin |
| `DELETE` | `/bookings/{id}` | Cancel booking | Owner/Admin |

## 🏗️ Project Structure

```
FlexBook/
├── app/
│   ├── db/                 # Database configuration and models
│   ├── routers/            # API route handlers for each resource
│   ├── schemas/            # Pydantic schemas for data validation
│   ├── utils/              # Utility functions (e.g., authentication, permissions)
│   ├── main.py             # Application entry point
│   └── services.py         # Business logic (e.g., booking conflict checks)
├── tests/                  # Test files for unit, integration, and load testing
├── alembic/                # Database migrations
├── sql/                    # SQL scripts
├── .gitignore              # Files and directories to be ignored by Git
├── alembic.ini             # Alembic configuration file
├── README.md               # Project documentation
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── .env                    # Environment variables (not committed to Git)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



---

**Built with ❤️ using FastAPI and modern Python tools**