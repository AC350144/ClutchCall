# ClutchCall

## About

ClutchCall is a sports-betting assistant that uses AI to suggest smart wagers and budget-friendly guidance. Users can copy, evaluate, and edit bets before adding them to a unified slip, with a desktop version for fast, seamless bet building.

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** - Build tool and dev server
- **React Router** - Navigation and routing
- **Tailwind CSS** - Styling
- **Radix UI** - Component library
- **Lucide React** - Icons

### Backend
- **Flask** - Python web framework
- **PyMySQL** - MySQL database connector
- **JWT** - Authentication tokens
- **bcrypt** - Password hashing
- **PyOTP** - Multi-factor authentication
- **scikit-learn** - Machine learning for budget recommendations
- **Pandas** - Data processing

### Database
- **MySQL** - Relational database

## Project Structure

```
ClutchCall/
├── frontend/          # React + TypeScript frontend
│   ├── components/    # React components
│   ├── src/          # Source files
│   └── styles/       # Global styles
├── backend/          # Flask backend
│   ├── app/          # Application logic
│   ├── models/       # ML models
│   ├── templates/    # HTML templates
│   └── tests/        # Backend tests
└── public/           # Static assets
```

## Prerequisites

- **Node.js** >= 20.19.0
- **Python** 3.x
- **MySQL** database server
- **npm** or **yarn**

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ClutchCall
```

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up MySQL database
# Run the SQL script to create tables
mysql -u your_username -p < database.sql

# Update database credentials in db.py if needed

# Run the Flask server
python main.py
```

The backend will run on `http://localhost:3000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will run on `http://localhost:5173` (or the next available port)

## Available Scripts

### Frontend

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Backend

```bash
# Run Flask server
python main.py
```

## Testing

### Frontend Tests

```bash
cd frontend
npx vitest
```

### Backend Tests

```bash
cd backend
python -m pytest tests/
```

## Features

- **User Authentication** - Secure login with JWT tokens
- **Multi-Factor Authentication** - MFA support with QR code setup
- **Bankroll Management** - Track betting balance and ROI
- **AI Recommendations** - Smart betting suggestions based on budget
- **Bet Slip** - Unified interface for managing bets
- **Chat Widget** - Interactive AI assistant for betting guidance
- **Responsive Design** - Works on desktop and mobile devices

## Database Schema

The application uses MySQL with the following main tables:
- `users` - User accounts and authentication
- `bankrolls` - User betting balance and statistics
- `sports` - Available sports
- `games` - Game/match information
- `bet_types` - Types of bets available

See `backend/database.sql` for the complete schema.
## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests to ensure everything works
4. Submit a pull request

