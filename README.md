# Health Data Management Platform

A comprehensive platform for managing personal and family health data, providing data visualization, analysis, and health assessments.

## Project Structure

```
.
├── backend/               # Flask backend application
├── frontend/             # React web application
├── mobile/               # React Native mobile application
├── database/             # Database migrations and schemas
└── docs/                 # Project documentation
```

## Tech Stack

- **Backend**: Python/Flask
- **Frontend**: React
- **Mobile**: React Native
- **Databases**: 
  - PostgreSQL (relational data)
  - MongoDB (document storage)
- **API**: RESTful

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- MongoDB 5+
- Docker (optional)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
flask run
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

### Mobile Setup

```bash
cd mobile
npm install
# For iOS
cd ios && pod install && cd ..
npm run ios
# For Android
npm run android
```

## Development

- Backend API runs on: http://localhost:5000
- Frontend dev server: http://localhost:3000
- API Documentation: http://localhost:5000/api/docs

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details