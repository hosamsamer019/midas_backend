# Smart Antibiogram System

A comprehensive web application for antibiogram data analysis with AI-powered antibiotic recommendations.

## Features

### Backend (Django REST Framework)
- **User Management**: Authentication and role-based access control
- **Data Models**: Bacteria, antibiotics, samples, test results, AI recommendations
- **AI Engine**: Machine learning model for antibiotic recommendations
- **File Upload**: Support for Excel/CSV data import with Cloudinary storage
- **Reports**: PDF/Excel report generation
- **Analytics**: Comprehensive data visualization endpoints

### Frontend (Next.js + TypeScript + TailwindCSS)
- **Dashboard**: Interactive charts and data visualization
- **Authentication**: JWT-based login system
- **File Upload**: Drag-and-drop interface for lab data
- **AI Recommendations**: Real-time antibiotic suggestions
- **Reports**: Generate and download PDF reports
- **Heatmap**: Resistance pattern visualization
- **Data Filtering**: Advanced filtering options

### AI Features
- **Machine Learning**: Random Forest classifier trained on historical data
- **Prediction API**: Real-time antibiotic recommendations
- **Model Training**: Automated retraining on new data
- **Accuracy Tracking**: Performance monitoring and metrics

## Tech Stack

### Backend
- Python 3.9
- Django 4.x
- Django REST Framework
- PostgreSQL
- Scikit-learn
- TensorFlow
- OpenCV + Tesseract (OCR)
- ReportLab (PDF generation)
- Cloudinary (File storage)

### Frontend
- Next.js 14
- TypeScript
- TailwindCSS
- Recharts (Data visualization)
- Axios (HTTP client)
- Framer Motion (Animations)

### DevOps
- Docker & Docker Compose
- PostgreSQL
- Nginx (Production)

## Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-antibiogram
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py load_initial_data
   python manage.py runserver
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Docker Setup

```bash
docker-compose up --build
```

## API Documentation

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration

### Data Endpoints
- `GET /api/stats/` - Dashboard statistics
- `GET /api/sensitivity-distribution/` - Sensitivity data
- `GET /api/antibiotic-effectiveness/` - Effectiveness metrics
- `GET /api/resistance-over-time/` - Time-series data
- `GET /api/resistance-heatmap/` - Heatmap data

### AI Endpoints
- `POST /api/ai/predict/` - Get antibiotic recommendations

### File Operations
- `POST /api/upload/` - Upload lab data files
- `GET /api/reports/{type}/` - Generate reports

## Usage

1. **Login** with your credentials
2. **Upload Data** via the file upload interface
3. **View Dashboard** for data visualization
4. **Get AI Recommendations** for specific bacteria
5. **Generate Reports** for analysis and sharing

## Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Production Setup
1. Configure environment variables
2. Set up PostgreSQL database
3. Configure Cloudinary for file storage
4. Build and deploy using Docker
5. Set up Nginx reverse proxy

### Environment Variables
```env
DATABASE_URL=postgresql://user:password@localhost/antibiogram
SECRET_KEY=your-secret-key
DEBUG=False
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on GitHub or contact the development team.
