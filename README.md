# 🤖 AI-Powered Mentoring System  
*A Smart Academic Mentorship and Career Guidance Platform*

---

## 🧭 Project Overview

The **AI-Powered Mentoring System** is a comprehensive web-based platform that integrates **Artificial Intelligence**, **data analytics**, and **role-based access** to enhance the academic mentoring process.  

It bridges the gap between **students**, **mentors**, and **administrators** by providing personalized learning insights, performance analysis, and intelligent mentor matching.  
Each user interacts with a dedicated dashboard, ensuring a tailored and secure experience.

---

## 🏗️ System Architecture

The system follows a **Modular Monolithic Architecture**, built using Flask and structured for scalability.  
All AI and analytics modules are isolated under the `src/` directory for maintainability.

### 🧩 Key Components
- **Flask Backend** — Manages routes, user sessions, and core logic.  
- **AI Services (src/)** — Handles mentor matching, ranking, and language model insights.  
- **Tailwind CSS Frontend** — Ensures a responsive, modern, and accessible interface.  
- **Data Service Layer** — Simulates a database using in-memory structures.  

---

## 👥 User Roles and Access Control

### 🧑‍🎓 **Student Portal**
- Personalized academic and career guidance.
- Access to AI-driven learning support and progress tracking.
- View of previous sessions, marks, and mentor feedback.

### 🧑‍🏫 **Mentor Dashboard**
- Manage mentees and sessions efficiently.
- Upload student marks and performance records.
- Access AI-powered session preparation insights and student analytics.

### 👩‍💼 **Admin Panel**
- Monitor system activity and AI analytics.
- Manage mentor verification and performance evaluation.
- Maintain data consistency across all modules.

Each role is securely validated during login using Flask sessions and role-based decorators.

---

## 💡 Feature Overview

Below is the detailed breakdown of all the major features in the system.

---

### 🎓 **A. Student Portal Features**

#### 1. AI Academic Advisor
- Provides intelligent responses to academic queries.
- Offers factually accurate and context-aware study support.
- Ensures academic compliance with a professional tone and disclaimer.

#### 2. Career Path Assessment
- Conducts questionnaire-based self-assessments.
- Generates preliminary AI reports on career suitability.
- Identifies strengths, improvement areas, and recommended disciplines.
- Marks reports as *“Pending Mentor Verification”* before approval.

#### 3. Personalized Learning Recommendations
- Suggests learning strategies and focus areas based on past performance.
- Highlights weak subjects and provides structured study paths.
- Updates recommendations dynamically after new data uploads.

#### 4. Performance Dashboard
- Displays semester-wise academic trends.
- Visualizes improvement metrics and comparative results.
- Offers an intuitive overview of progress.

#### 5. AI Resource Suggestion
- Curates high-quality online materials like tutorials and research papers.
- Adapts recommendations according to query history and interests.

---

### 🧑‍🏫 **B. Mentor Hub Features**

#### 1. Mentor Session Management
- Lists assigned students and their academic summaries.
- Tracks scheduled, completed, and upcoming mentoring sessions.
- Maintains notes and records for each interaction.

#### 2. AI Session Preparation Tips
- Generates concise, 3-point session insights using AI.
- Helps mentors prepare personalized strategies for each mentee.
- Encourages data-driven mentoring outcomes.

#### 3. Marks Upload System
- Enables CSV/Excel upload of student marks.
- Automatically integrates the latest academic performance.
- Provides instant access to updated student profiles.

#### 4. Mentor Feedback Collection
- Collects anonymous student feedback post-session.
- Displays mentor performance summaries.
- Uses feedback data for AI-based ranking.

#### 5. Student Progress Overview
- Shows academic growth trends for each student.
- Highlights improvement patterns and risk indicators.
- Helps mentors recommend personalized learning plans.

---

### 📊 **C. AI Core Features**

#### 1. AI Mentor Matching
- Matches students with suitable mentors using keyword similarity.
- Compares student “weakness areas” with mentor “expertise fields.”
- Provides ranked mentor recommendations for approval.

#### 2. Mentor Performance Ranking
- Calculates mentor scores based on feedback and engagement.
- Adjusts for mentors with fewer reviews using fairness weighting.
- Displays a ranked leaderboard accessible by admin.

#### 3. Career Insight Generation
- Produces AI-generated summaries of career trends.
- Highlights emerging opportunities and required skill sets.
- Assists mentors in guiding students effectively.

#### 4. Analytics and Reporting
- Aggregates marks, feedback, and mentoring session data.
- Generates summary reports for departments and admin view.
- Displays data-driven insights through visual analytics.

---

### ⚙️ **D. Admin Control Panel Features**

#### 1. Mentor Approval System
- Lists pending mentor registrations.
- Allows approval, rejection, or follow-up actions.
- Maintains a verified mentor database.

#### 2. System Analytics Dashboard
- Displays key performance metrics for all users.
- Tracks engagement rates and active mentoring sessions.
- Highlights insights such as top-performing mentors or common student issues.

#### 3. Data Oversight and Integrity
- Centralized view of all system data and user roles.
- Allows admin to audit, archive, or manage datasets.
- Ensures data compliance and consistency across all modules.

#### 4. AI Report Monitoring
- Reviews all AI-generated reports for accuracy and ethical compliance.
- Flags and tracks unverified or inconsistent reports.
- Allows admin to approve finalized insights before publication.

---

### 🌐 **E. System-Wide Features**

#### 1. Role-Based Access Control
- Distinct dashboards for each user role.
- Restricts unauthorized access to sensitive information.
- Provides contextual navigation and secure session handling.

#### 2. Unified Dashboard Interface
- A single responsive design for all user roles.
- Automatically adapts menu items based on login type.
- Built using Tailwind CSS for clean and mobile-friendly UI.

#### 3. Data Validation and Integrity
- Enforces input validation for uploads and feedback.
- Prevents data duplication and inconsistent states.
- Ensures reliable and accurate AI outputs.

#### 4. Security and Privacy
- Uses environment variables for secret keys and API credentials.
- Protects user data with secure sessions and role boundaries.
- Adheres to ethical AI and data protection standards.

---

## 📦 Production & Deployment Features

| Feature | Description |
| :------ | :----------- |
| **Gunicorn Support** | Configured for deployment with a production-grade WSGI server. |
| **Environment Configuration** | Sensitive keys managed via environment variables. |
| **Dependency Management** | All libraries listed in `requirements.txt`. |
| **Procfile Integration** | Simplifies deployment to Heroku, Render, or AWS. |

---

## 🧠 Future Enhancements

| Planned Feature | Description |
| :--------------- | :----------- |
| **Database Integration** | Replace in-memory data with SQLAlchemy or MongoDB. |
| **Real-Time Chat** | Implement live mentor-student chat using WebSockets. |
| **AI Sentiment Analysis** | Analyze student feedback to detect emotional tone. |
| **Automated Notifications** | Add email or in-app alerts for reports and updates. |
| **Interactive Analytics** | Integrate Chart.js or Plotly for advanced data visuals. |

---

## 🧾 Summary

The **AI-Powered Mentoring System** is an innovative academic support tool that combines **AI intelligence**, **data visualization**, and **mentorship management** into one platform.  

It empowers:
- **Students** with personalized career and learning guidance.  
- **Mentors** with AI-assisted preparation and actionable insights.  
- **Admins** with analytics-driven control over the mentoring ecosystem.  

By merging **AI reasoning** with **human mentorship**, this system promotes a smarter, data-driven educational environment.

---

### 🏁 Project Status
✅ **Completed (Stable Release)**  
🚀 **Ready for Deployment and Future Expansion**

---
### 🧑‍💻 Developed By  
<p align="center">
  <a href="https://github.com/premkumar-epic" target="_blank" style="text-decoration:none;">
    <b>Prem Kumar</b> / <b>Mr. EPIC</b>
  </a>
</p>

---

## 📬 How to Reach Me  
<p align="center">
  <a href="mailto:premkumar.dev25@gmail.com">
    <img src="https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white">
  </a>
  <a href="https://www.linkedin.com/in/premkumar-25-8055p/">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white">
  </a>
  <a href="https://twitter.com/PremKumar253">
    <img src="https://img.shields.io/badge/Twitter-000000?style=for-the-badge&logo=x&logoColor=white">
  </a>
  <a href="https://www.instagram.com/prem.kumar.2.5/">
    <img src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white">
  </a>
  <a href="https://buymeacoffee.com/premkumar.dev">
    <img src="https://img.shields.io/badge/Buy_Me_a_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black">
  </a>
</p>
