# 🎓 Sage Tutoring Report Assistant

> An AI-powered web application to help tutors write, organize, and manage session reports efficiently

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 14+](https://img.shields.io/badge/node-14+-green.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- 📝 **AI Report Generation** - Generate professional tutoring reports in your unique writing style
- 👥 **Student Management** - Track student information, schedules, and session history
- 📅 **Smart Calendar** - Visual weekly calendar showing sessions and report status
- 🧠 **Session Continuity** - AI automatically extracts reminders from previous sessions
- ✏️ **Flexible Editing** - Choose between full AI assistance or minimal grammar-only edits
- 💾 **Unified Timeline** - See all created and uploaded reports in one chronological view
- 🔄 **Schedule Management** - Cancel, reschedule, or add one-time sessions
- 📊 **Report Tracking** - Visual status indicators (draft, sent, uploaded)
- 👤 **Tutor Profiles** - Automatic signature with optional contact information
- 🎯 **Style Learning** - Upload past reports to train the AI in your writing style

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Node.js 14+** - [Download here](https://nodejs.org/)
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/sage-reports.git
cd sage-reports
```

2. **Set up the backend**
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

3. **Set up the frontend**
```bash
cd frontend
npm install
cd ..
```

4. **Configure your API key**
```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your-actual-api-key-here
```

5. **Launch the application**
```bash
./launch.sh
```

The app will automatically open in your browser at `http://localhost:3000`

### Stopping the Application

```bash
./stop.sh
```

---

## 📖 Usage Guide

### First Time Setup

1. **Configure Your Profile** (Settings page)
   - Add your name, phone, and email
   - These will appear in report signatures

2. **Upload Sample Reports** (Settings page)
   - Upload 10-20+ of your past reports
   - The AI learns your writing style from these
   - The more samples, the better the results

3. **Add Students** (Students page)
   - Enter student details (name, grade, subject)
   - Add school, teacher, and parent information
   - Set recurring schedule (e.g., "Mondays 4pm, Thursdays 6pm")

### Creating a New Report

1. Click **"New Report"** from the dashboard
2. Select a student
3. Enter the session date and duration
4. Add your session notes (what you worked on, student progress, etc.)
5. Choose your AI mode:
   - **Full AI**: Expands your notes into a complete report
   - **Minimal Editing**: Just fixes grammar while keeping your exact wording
6. Click **"Generate Report with AI"**
7. Review, edit, and save

### Managing Your Calendar

- View all scheduled sessions in a visual weekly format
- Click the **⋮** menu on any session to:
  - Write/edit a report
  - Reschedule the session
  - Cancel the session
  - Delete the session
- Add one-time sessions with the **"+ Add Session"** button
- Color-coded status:
  - 🟢 Green = Report completed
  - 🔴 Red = Report needed
  - ⚪ Gray = Cancelled

---

## 🏗️ Project Structure

```
sage-reports/
├── backend/                 # Flask API server
│   ├── app.py              # Main application & routes
│   ├── ai_service.py       # OpenAI integration
│   ├── database.py         # SQLAlchemy models
│   ├── migrations/         # Database migration scripts
│   └── database/           # SQLite database files
├── frontend/               # React web interface
│   ├── src/
│   │   ├── pages/         # Main application pages
│   │   ├── components/    # Reusable UI components
│   │   └── services/      # API client
│   └── package.json
├── docs/                   # Documentation
│   ├── features/          # Feature-specific docs
│   ├── development/       # Development notes
│   ├── DAILY_USE.md       # Day-to-day usage guide
│   └── USER_GUIDE.md      # Complete user manual
├── logs/                   # Application logs
├── requirements.txt        # Python dependencies
├── launch.sh              # One-click startup script
└── stop.sh                # Shutdown script
```

---

## 🛠️ Technology Stack

**Backend:**
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [OpenAI API](https://openai.com/api/) - AI report generation
- SQLite - Database

**Frontend:**
- [React](https://react.dev/) - UI framework
- [Vite](https://vitejs.dev/) - Build tool
- [Tailwind CSS](https://tailwindcss.com/) - Styling

---

## 📋 Development

### Running in Development Mode

**Backend (in one terminal):**
```bash
source venv/bin/activate
python backend/app.py
```

**Frontend (in another terminal):**
```bash
cd frontend
npm run dev
```

### Database Migrations

Database migrations are located in `backend/migrations/`. To run a migration:

```bash
source venv/bin/activate
python backend/migrations/migrate_xxx.py
```

---

## 🔐 Security Notes

- **Never commit your `.env` file** - It contains your API key
- The `.gitignore` file already excludes sensitive files
- Your database files are stored locally and not committed to GitHub
- API keys should have rate limits and spending caps enabled

---

## 📚 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get up and running fast
- **[User Guide](docs/USER_GUIDE.md)** - Complete usage instructions
- **[Daily Use](docs/DAILY_USE.md)** - Common workflows
- **[Changelog](CHANGELOG.md)** - Development history and updates
- **[Features](docs/features/)** - Detailed feature documentation

---

## 🤝 Contributing

This is a personal project, but if you find it useful and want to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [OpenAI's GPT models](https://openai.com/)
- UI inspired by modern tutoring platforms
- Created to streamline tutoring session documentation

---

## 📞 Support

Having issues? Check these resources:

- **[Troubleshooting Guide](docs/USER_GUIDE.md#troubleshooting)**
- **[GitHub Issues](https://github.com/yourusername/sage-reports/issues)**
- Review the logs in the `logs/` directory

---

## 🎯 Roadmap

- [ ] Bulk CSV import for historical reports
- [ ] Email integration for sending reports directly
- [ ] Analytics dashboard for session insights
- [ ] Export to PDF with custom templates
- [ ] Multi-tutor support for tutoring centers
- [ ] Mobile-responsive improvements

---

<div align="center">

**Made with ❤️ for tutors who want to spend more time teaching and less time on paperwork**

[⭐ Star this repo](https://github.com/yourusername/sage-reports) if you find it helpful!

</div>
