# AutoEDA Studio

A beautiful, interactive frontend for automated Exploratory Data Analysis and preprocessing.

## Features

- **File Upload**: Drag-and-drop CSV upload with instant processing
- **Column Management**: Interactive selection and removal of unnecessary columns
- **Missing Values**: AI-powered suggestions for handling missing data
- **Outlier Detection**: Intelligent outlier detection and handling using IQR method
- **Correlation Analysis**: Automatic detection and removal of highly correlated features
- **Categorical Encoding**: Smart encoding suggestions (One-Hot or Label Encoding)
- **Feature Scaling**: Automatic scaling with Standard or MinMax scalers
- **Visualizations**: Interactive correlation heatmaps and analysis
- **Export**: Download cleaned CSV and Jupyter Notebook with reproducible code

## Setup

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+ with FastAPI backend

### Frontend Setup

```bash
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Backend Setup

Your FastAPI backend should be running on `http://localhost:8000`. Place your Python backend code in a separate directory and run:

```bash
pip install fastapi uvicorn pandas numpy scikit-learn matplotlib seaborn
uvicorn main:app --reload
```

Where `main.py` contains your FastAPI application code.

## Usage

1. **Upload Dataset**: Start by uploading a CSV file
2. **Review Columns**: See all columns with their types, uniqueness, and missing percentages
3. **Drop Columns**: Optionally remove unnecessary columns
4. **Handle Missing Values**: Review AI suggestions and customize if needed
5. **Handle Outliers**: Apply capping or row removal based on suggestions
6. **Check Correlations**: Automatically remove highly correlated features
7. **Encode Categories**: Convert text features to numbers for ML models
8. **Scale Features**: Normalize numerical features
9. **Analyze**: View correlation heatmaps and other visualizations
10. **Download**: Export cleaned data and reproducible Python code

## Design Features

- Modern gradient backgrounds and glassmorphism effects
- Smooth animations and transitions
- Responsive design for all screen sizes
- Step-by-step progress indicator
- Real-time data shape tracking
- Color-coded suggestions and warnings
- Interactive customization options

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Icons**: Lucide React
- **Backend**: FastAPI (Python)
- **Styling**: Custom animations, gradients, and transitions

## Configuration

Backend API URL can be configured in `.env`:

```
VITE_API_URL=http://localhost:8000
```

## Color Scheme

The application uses a beautiful, modern color palette:
- Primary: Blue and Cyan gradients
- Success: Green and Emerald
- Warning: Orange and Amber
- Danger: Red and Rose
- Neutral: Slate grays

Intentionally avoiding purple/indigo hues for a fresh, professional look.
