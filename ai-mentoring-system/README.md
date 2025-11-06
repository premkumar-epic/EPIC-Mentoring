# 📘 AI-Powered Mentoring System

An intelligent platform designed to enhance academic mentoring by integrating AI-driven insights, data analytics, and role-based dashboards.

## 🧭 Project Overview

The AI-Powered Mentoring System bridges the gap between students, mentors, and administrators by offering:
- Personalized academic support
- Automated mentor recommendations
- Performance tracking
- Career guidance

The system ensures every user — whether a student, mentor, or admin — receives a customized experience, backed by intelligent data analysis.

## 🏗️ System Architecture

The application follows a **Modular Monolithic Architecture**, built around the Flask framework. Each module is independently structured to handle specific tasks.

### Key Components

- **Backend** — Core framework handling routing, user roles, and business logic
- **AI Services** — Dedicated modules for AI functionalities (mentor matching, ranking, natural language assistance)
- **Tailwind CSS Frontend** — Responsive interface using modern UI styling
- **Data Service Layer** — Centralized manager that maintains and processes all in-memory data structures

## 👥 User Roles

### 🧑‍🎓 Student Portal
- Personalized academic and career guidance
- Real-time AI support for learning and improvement
- Access to historical performance and feedback reports

### 🧑‍🏫 Mentor Dashboard
- Tools to manage mentees and mentoring sessions
- Access to AI-powered preparation insights
- Upload and analyze student performance data
- Provide assessments and action plans

### 👩‍💼 Admin Panel
- Manage all users, mentors, and student data
- Review AI-generated analytics and performance reports
- Approve or reject mentor applications
- Monitor system efficiency and data trends

## ✨ Features

### Student Portal Features
1. **AI Academic Advisor** - Instant, AI-generated academic help
2. **Career Path Assessment** - Psychometric-style assessments with personalized reports
3. **Personalized Learning Recommendations** - Subject-specific study materials
4. **Performance Dashboard** - Visualize academic trends and improvements
5. **AI Resource Suggestion** - Curated learning resources

### Mentor Hub Features
1. **Mentor Session Management** - View and schedule sessions
2. **AI Session Preparation Tips** - Context-specific preparation notes
3. **Marks Upload System** - Upload performance data via CSV
4. **Mentor Feedback Collection** - Review student satisfaction
5. **Student Progress Overview** - Consolidated performance history

### Admin Panel Features
1. **Mentor Approval System** - Approve/reject mentor applications
2. **System Analytics Dashboard** - Visualize engagement and performance
3. **Data Oversight** - View all users and their activity
4. **AI Report Monitoring** - Track AI-generated reports

### AI Core Features
1. **AI Mentor Matching** - Keyword-based similarity matching
2. **Mentor Performance Ranking** - Calculate mentor scores based on feedback
3. **Career Insight Generation** - AI-generated career summaries
4. **Analytics and Reporting** - Aggregated feedback and statistics

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or navigate to the project directory:**
   ```bash
   cd ai-mentoring-system
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

## 🔐 Default Login Credentials

The system comes with sample accounts for testing:

### Admins (2 accounts)
- **Admin User**
  - Email: `admin@example.com`
  - Password: `admin123`

- **Super Admin**
  - Email: `superadmin@example.com`
  - Password: `admin456`

### Mentors (5 accounts - 4 approved, 1 pending)
- **Dr. Sarah Johnson** (Approved)
  - Email: `sarah@example.com`
  - Password: `mentor123`
  - Expertise: Mathematics, Physics, Computer Science
  - Rating: 4.5

- **Prof. Michael Chen** (Approved)
  - Email: `michael@example.com`
  - Password: `mentor456`
  - Expertise: Chemistry, Biology, Engineering
  - Rating: 4.8

- **Dr. Robert Williams** (Approved)
  - Email: `robert@example.com`
  - Password: `mentor101`
  - Expertise: English, Literature, History
  - Rating: 4.7

- **Prof. Lisa Anderson** (Approved)
  - Email: `lisa@example.com`
  - Password: `mentor202`
  - Expertise: Business, Economics, Finance
  - Rating: 4.6

- **Dr. Emily Rodriguez** (Pending Approval)
  - Email: `emily@example.com`
  - Password: `mentor789`
  - Expertise: Psychology, Sociology, Education
  - Status: Pending (for testing approval workflow)

### Students (50 accounts)
The system includes **50 sample students** with diverse profiles, marks, and mentor assignments.

**Login Pattern:**
- Email format: `student001@example.com` through `student050@example.com`
- Password format: `student001` through `student050`
- Example: `student001@example.com` / `student001`

**Student Distribution:**
- **35 students** are assigned to mentors (distributed across approved mentors)
- **15 students** are unmatched (available for mentor matching)
- Each student has:
  - Unique strengths and weakness areas
  - 3-5 sample subject marks
  - Varied performance data for testing

**Quick Test Accounts:**
- **Student 1**: `student001@example.com` / `student001`
- **Student 2**: `student002@example.com` / `student002`
- **Student 3**: `student003@example.com` / `student003`
- ... and so on up to `student050@example.com` / `student050`

## 📁 Project Structure

```
ai-mentoring-system/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── services/
│   ├── __init__.py
│   ├── data_service.py      # Data management layer
│   └── ai_service.py        # AI functionality
├── utils/
│   ├── __init__.py
│   └── auth.py             # Authentication utilities
└── templates/
    ├── base.html           # Base template
    ├── index.html          # Home page
    ├── login.html          # Login page
    ├── register.html       # Registration page
    ├── student/           # Student portal templates
    ├── mentor/            # Mentor dashboard templates
    └── admin/             # Admin panel templates
```

## 🔧 Configuration

### Environment Variables

For production, set the following environment variable:
```bash
export SECRET_KEY='your-secret-key-here'
```

The application uses a default secret key for development (not recommended for production).

## 📊 CSV Upload Format

For mentor marks upload, use the following CSV format:

```csv
student_id,subject,marks,semester,date
1,Mathematics,85,Fall 2024,2024-09-15
1,Physics,78,Fall 2024,2024-09-20
```

## 🛡️ Security Features

- Role-based access control (RBAC)
- Secure session handling
- Password hashing using Werkzeug
- Access-level restrictions per user role

## 🎨 UI/UX

- Modern, responsive design using Tailwind CSS
- Role-based navigation
- Mobile-friendly interface
- Accessible color schemes and icons

## 📝 Notes

- **Data Storage**: Currently uses in-memory data structures. For production, consider migrating to a database (PostgreSQL, MySQL, etc.)
- **AI Integration**: The current implementation uses rule-based AI. For production, integrate with OpenAI API or similar LLM services
- **File Uploads**: CSV upload functionality is implemented. Excel support can be added using `openpyxl` or `pandas`

## 🔮 Future Enhancements

- Database integration (SQLAlchemy)
- Real LLM API integration (OpenAI, Anthropic)
- Email notifications
- Advanced analytics and reporting
- Mobile app support
- Real-time chat functionality

## 📄 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📧 Support

For questions or support, please refer to the project documentation or create an issue in the repository.

---

**Built with ❤️ using Flask and Tailwind CSS**

