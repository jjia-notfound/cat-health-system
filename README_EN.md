# Cat Health Management System 🐱

A comprehensive web-based system for tracking and analyzing your cat's health data, with AI-powered disease risk assessment.

## ✨ Features

- 📊 **Health Data Tracking**: Monitor water intake, food consumption, urination, defecation, vomiting, diarrhea, and weight
- 🤖 **AI Disease Detection**: Machine learning models to assess CKD, pancreatitis, and parasite risks
- 📱 **User-Friendly Interface**: Clean, responsive web interface optimized for mobile devices
- 📈 **Data Visualization**: Charts and graphs for health trends analysis
- 🔄 **Multiple Input Methods**: CSV file upload or manual data entry
- 🏥 **Health Records**: Complete history of health assessments
- 👤 **Multi-Cat Support**: Manage multiple cats in one system

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/cat-health-system.git
cd cat-health-system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Start the application**
```bash
python start.py
```

4. **Access the application**
Open your browser and go to: http://localhost:8000

### Docker (Optional)
```bash
docker build -t cat-health .
docker run -p 8000:8000 cat-health
```

## 📋 Data Format

### CSV File Structure
Your CSV file should contain these columns:
- `Date`: Format YYYY-MM-DD
- `Water(ml)`: Daily water intake in milliliters
- `Food(g)`: Daily food consumption in grams
- `Urination`: Number of urination times per day
- `Defecation`: Number of defecation times per day
- `Vomiting`: Number of vomiting incidents per day
- `Diarrhea`: Number of diarrhea incidents per day
- `Weight(kg)`: Cat's weight in kilograms

### Example CSV
```csv
Date,Water(ml),Food(g),Urination,Defecation,Vomiting,Diarrhea,Weight(kg)
2024-01-01,200,50,3,2,0,0,4.2
2024-01-02,180,45,2,1,1,0,4.1
```

## 🎯 Usage Guide

### 1. Create a Cat Profile
- Click "Add New Cat"
- Enter cat's name and optional avatar
- Save the profile

### 2. Upload Health Data
- Go to your cat's detail page
- Click "Upload Data"
- Choose CSV file upload or manual entry
- Data will be processed and stored

### 3. Health Assessment
- Click "Health Check" to run AI analysis
- View detailed risk assessment results
- Check historical health records

### 4. Monitor Trends
- View daily health data in table format
- Analyze trends over time
- Export data for external analysis

## 🔧 Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: Bootstrap 5, jQuery
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn
- **Visualization**: Chart.js
- **Database**: CSV file storage (simple and portable)

## 🎨 Screenshots

*Screenshots will be added here*

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with love for cat owners
- Inspired by the need for better pet health monitoring
- Thanks to the open-source community

## 📞 Support

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join GitHub Discussions for questions
- **Email**: [your-email@example.com]

---

**Made with ❤️ for cats and their humans**