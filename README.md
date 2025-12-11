# Calculations API - BREAD Operations

A full-stack web application implementing BREAD (Browse, Read, Edit, Add, Delete) operations for calculations with user authentication, built with FastAPI, PostgreSQL, and modern web technologies.

## 🚀 Features

- **Complete BREAD Operations** for calculations
  - **Browse**: View all calculations for logged-in user
  - **Read**: Get details of a specific calculation
  - **Edit**: Update existing calculations (PUT/PATCH)
  - **Add**: Create new calculations with various operations
  - **Delete**: Remove calculations

- **User Authentication & Authorization**
  - Secure user registration and login
  - JWT token-based authentication
  - Password hashing with bcrypt
  - User-specific calculation isolation

- **Mathematical Operations**
  - Addition
  - Subtraction
  - Multiplication
  - Division (with zero-division protection)

- **Modern Front-End**
  - Responsive design
  - Form validation
  - Real-time updates
  - User-friendly interface

- **Testing & CI/CD**
  - Comprehensive Playwright E2E tests
  - GitHub Actions automation
  - Docker containerization
  - Automated Docker Hub deployment

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional)
- Node.js (for Playwright)

## 🛠️ Installation & Setup

### Option 1: Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd WEBAPI_ASS14
   ```

2. **Configure environment variables**
   - Review the `.env` file
   - Update `SECRET_KEY` for production

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Application: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Interactive API: http://localhost:8000/redoc

### Option 2: Local Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd WEBAPI_ASS14
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   ```bash
   # Install PostgreSQL and create database
   createdb calculations_db
   ```

5. **Configure environment variables**
   ```bash
   # Update .env file with your database URL
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/calculations_db
   SECRET_KEY=your-secret-key-change-in-production-min-32-chars-long
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access the application**
   - Application: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🧪 Running Tests

### Local Testing

1. **Install test dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   playwright install-deps
   ```

2. **Start the application** (in a separate terminal)
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Run Playwright tests**
   ```bash
   pytest tests/test_e2e.py -v
   ```

### Test Coverage

The test suite includes:

- **Authentication Tests**
  - ✅ Successful registration
  - ✅ Duplicate username handling
  - ✅ Invalid email format
  - ✅ Successful login
  - ✅ Wrong password handling

- **BREAD Operations Tests**
  - ✅ Add calculation (positive)
  - ✅ Division by zero (negative)
  - ✅ Browse all calculations
  - ✅ Read specific calculation
  - ✅ Edit calculation (positive)
  - ✅ Delete calculation
  - ✅ User isolation

- **Edge Cases**
  - ✅ Decimal numbers
  - ✅ Negative numbers
  - ✅ Large numbers

## 🔄 CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment:

1. **On Push/Pull Request**
   - Sets up Python and PostgreSQL
   - Installs dependencies
   - Runs Playwright E2E tests
   - Uploads test results

2. **On Push to Main/Master** (after tests pass)
   - Builds Docker image
   - Pushes to Docker Hub
   - Tags with latest and commit SHA

### Setting Up GitHub Actions

1. **Add secrets to GitHub repository**
   - Go to Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `DOCKER_USERNAME`: Your Docker Hub username
     - `DOCKER_PASSWORD`: Your Docker Hub password/token

2. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

3. **Monitor workflow**
   - Go to Actions tab in GitHub
   - View workflow runs and results

## 🐳 Docker Hub

After successful CI/CD pipeline execution, the Docker image is automatically pushed to Docker Hub.

**Pull and run the image:**
```bash
# Pull the image
docker pull bhavanavuttunoori/calculations-api:latest

# Run with PostgreSQL
docker-compose up
```

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123"
}
```

#### Login
```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=securepass123
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

### Calculation Endpoints

#### Browse - Get All Calculations
```http
GET /calculations/
Authorization: Bearer <token>
```

#### Read - Get Specific Calculation
```http
GET /calculations/{id}
Authorization: Bearer <token>
```

#### Add - Create Calculation
```http
POST /calculations/
Authorization: Bearer <token>
Content-Type: application/json

{
  "operation": "add",
  "operand1": 10,
  "operand2": 5
}
```

Operations: `add`, `subtract`, `multiply`, `divide`

#### Edit - Update Calculation
```http
PUT /calculations/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "operation": "multiply",
  "operand1": 8,
  "operand2": 3
}
```

Or partial update:
```http
PATCH /calculations/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "operand1": 15
}
```

#### Delete - Remove Calculation
```http
DELETE /calculations/{id}
Authorization: Bearer <token>
```

## 🏗️ Project Structure

```
WEBAPI_ASS14/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database models and config
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   └── routes/
│       ├── __init__.py
│       ├── auth_routes.py   # Auth endpoints
│       └── calculation_routes.py  # BREAD endpoints
├── static/
│   ├── index.html           # Front-end interface
│   ├── styles.css           # Styling
│   └── app.js               # Client-side logic
├── tests/
│   ├── __init__.py
│   └── test_e2e.py          # Playwright E2E tests
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # GitHub Actions workflow
├── .env                     # Environment variables
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── README.md
```

## 🔒 Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Secure token-based authentication
- **User Isolation**: Users can only access their own calculations
- **Input Validation**: Pydantic models validate all inputs
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **CORS Configuration**: Configurable cross-origin requests

## 🎯 Learning Outcomes Achieved

- ✅ **CLO3**: Python applications with automated testing (Playwright)
- ✅ **CLO4**: GitHub Actions CI/CD with automated tests and Docker builds
- ✅ **CLO9**: Docker containerization
- ✅ **CLO10**: REST API creation, consumption, and testing
- ✅ **CLO11**: SQL database integration (PostgreSQL with SQLAlchemy)
- ✅ **CLO12**: JSON serialization/deserialization with Pydantic
- ✅ **CLO13**: Secure authentication (JWT, bcrypt hashing)

## 📸 Screenshots Guide

For assignment submission, capture:

1. **GitHub Actions Workflow**
   - Navigate to Actions tab
   - Show successful workflow run (green checkmark)
   - Capture test results

2. **Docker Hub Deployment**
   - Show Docker Hub repository
   - Display pushed image with tags

3. **Application Functionality**
   - Registration form
   - Login screen
   - Create calculation form
   - List of calculations
   - Edit calculation modal
   - Delete confirmation
   - API documentation (/docs)

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs db

# Recreate database
docker-compose down -v
docker-compose up --build
```

### Port Already in Use
```bash
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Test Failures
```bash
# Ensure application is running
curl http://localhost:8000/health

# Clear test data
# Recreate database
docker-compose down -v && docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is created for educational purposes as part of Module 14 Assignment.

## 👤 Author

**Student Name**: [Your Name]
**Course**: Web API Development
**Assignment**: Module 14 - BREAD Functionality for Calculations

## 🔗 Links

- Docker Hub: https://hub.docker.com/r/bhavanavuttunoori/calculations-api
- GitHub Repository: https://github.com/BhavanaVuttunoori/assignment14
- API Documentation: http://localhost:8000/docs

---

**Note**: Remember to update the SECRET_KEY in `.env` for production deployments and never commit sensitive credentials to version control.
