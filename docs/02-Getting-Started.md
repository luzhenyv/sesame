# Getting Started

This guide helps new team members set up their development environment and start contributing to the User Health Data Management Platform.

## Development Environment Setup

### Prerequisites

- **Git**: Version control system
- **Python 3.8+**: For backend development
- **Node.js 16+**: For frontend development
- **Docker**: For containerized development and testing
- **MongoDB**: For document storage
- **PostgreSQL**: For relational data storage

### Repository Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourorganization/health-data-platform.git
   cd health-data-platform
   ```

2. Set up Git hooks for code quality:
   ```bash
   cp scripts/pre-commit .git/hooks/
   chmod +x .git/hooks/pre-commit
   ```

## Backend Setup

### Flask API Setup

1. Create a Python virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your local configuration.

4. Initialize the database:
   ```bash
   flask db upgrade
   ```

5. Run the development server:
   ```bash
   flask run --debug
   ```
   The API will be available at `http://localhost:5000`.

### Database Setup

1. Start MongoDB:
   ```bash
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

2. Start PostgreSQL:
   ```bash
   docker run -d -p 5432:5432 --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -e POSTGRES_DB=healthdb postgres:latest
   ```

## Frontend Setup

### Web Application (React)

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env.local
   ```
   Edit `.env.local` with your local configuration.

3. Start the development server:
   ```bash
   npm run dev
   ```
   The web application will be available at `http://localhost:3000`.

### Mobile Application (React Native)

1. Install dependencies:
   ```bash
   cd mobile
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your local configuration.

3. Start the Metro bundler:
   ```bash
   npm start
   ```

4. Run on iOS:
   ```bash
   npm run ios
   ```
   
5. Run on Android:
   ```bash
   npm run android
   ```

## Third-Party Services Setup

### AWS Services

1. Create an AWS account if you don't have one.
2. Set up IAM user with necessary permissions.
3. Configure AWS CLI:
   ```bash
   aws configure
   ```
   Enter your AWS access key, secret key, and region.

### OCR Processing

1. Install Tesseract OCR:
   ```bash
   # On macOS
   brew install tesseract
   
   # On Ubuntu
   sudo apt-get install tesseract-ocr
   
   # On Windows
   # Download installer from https://github.com/UB-Mannheim/tesseract/wiki
   ```

2. Verify installation:
   ```bash
   tesseract --version
   ```

## Development Workflow

### Branching Strategy

We follow a modified GitFlow workflow:

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `release/*`: Release preparation

Example of starting a new feature:
```bash
git checkout develop
git pull
git checkout -b feature/user-authentication
```

### Pull Request Process

1. Create a pull request from your feature branch to `develop`.
2. Ensure the CI pipeline passes.
3. Request review from at least one team member.
4. Address review comments.
5. Merge once approved.

### Code Quality Tools

- **ESLint**: JavaScript/TypeScript linting
  ```bash
  cd frontend
  npm run lint
  ```

- **Flake8**: Python linting
  ```bash
  cd backend
  flake8
  ```

- **Prettier**: Code formatting
  ```bash
  cd frontend
  npm run format
  ```

## Testing

### Backend Testing

Run the backend tests:
```bash
cd backend
pytest
```

### Frontend Testing

Run the frontend tests:
```bash
cd frontend
npm test
```

### Mobile Testing

Run the mobile app tests:
```bash
cd mobile
npm test
```

## Documentation

- API documentation is available at `http://localhost:5000/docs` when the backend is running.
- Frontend component documentation is available at `http://localhost:6006` after running:
  ```bash
  cd frontend
  npm run storybook
  ```

## Getting Help

- **Slack Channel**: #health-platform-dev
- **Wiki**: https://wiki.yourorganization.com/health-platform
- **Issues**: https://github.com/yourorganization/health-data-platform/issues

## Next Steps

1. Review the [Project Overview](./01-Project-Overview.md) to understand the system architecture.
2. Explore the [Requirements and Features](./03-Requirements_and_Features.md) to learn about the product specifications.
3. Check the [Roadmap and Iteration Plan](./05-Roadmap_and_Iteration.md) to understand the development timeline. 