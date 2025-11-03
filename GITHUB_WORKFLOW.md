# 🚀 GitHub Workflow Guide

This guide explains how to manage your Sage Reports codebase on GitHub, including the initial upload and ongoing updates.

---

## 📤 Initial Upload to GitHub

### 1. Create a New GitHub Repository

1. Go to [github.com](https://github.com) and log in
2. Click the **"+"** icon in the top-right → **"New repository"**
3. Fill in the details:
   - **Repository name**: `sage-reports` (or your preferred name)
   - **Description**: "AI-powered tutoring report assistant"
   - **Visibility**: Choose **Public** (to share) or **Private** (personal use)
   - ⚠️ **DO NOT** check "Initialize with README" (we already have one)
4. Click **"Create repository"**

### 2. Connect Your Local Code to GitHub

```bash
# Navigate to your project directory
cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports"

# Set your Git identity (if not already done)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files to git
git add .

# Create your first commit
git commit -m "Initial commit: Sage Reports v1.0 - AI-powered tutoring assistant"

# Link to your GitHub repository (replace with your actual URL)
git remote add origin https://github.com/yourusername/sage-reports.git

# Push your code to GitHub
git branch -M main
git push -u origin main
```

### 3. Verify the Upload

1. Refresh your GitHub repository page
2. You should see all your files uploaded
3. The README.md will display automatically on the main page

---

## 🔄 Making Updates and Pushing Changes

### Simple Workflow (Most Common)

After making changes to your code:

```bash
# 1. Check what files you changed
git status

# 2. Add all changed files
git add .

# 3. Commit with a descriptive message
git commit -m "Add new feature: student bulk import"

# 4. Push to GitHub
git push
```

### Best Practices for Commit Messages

Use clear, descriptive commit messages:

**Good:**
- ✅ `"Add email integration for sending reports"`
- ✅ `"Fix: Calendar not showing cancelled sessions"`
- ✅ `"Update AI prompt for better report quality"`
- ✅ `"Docs: Update installation instructions"`

**Bad:**
- ❌ `"Update"`
- ❌ `"Fixed stuff"`
- ❌ `"Changes"`

### Commit Message Prefixes

Use these prefixes for clarity:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - UI/formatting changes
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

**Examples:**
```bash
git commit -m "feat: Add PDF export functionality"
git commit -m "fix: Resolve timezone issues in calendar"
git commit -m "docs: Add troubleshooting section to README"
```

---

## 📅 Recommended Update Workflow

### Daily/After Each Work Session

```bash
# 1. See what you changed
git status
git diff

# 2. Add specific files (or use git add . for all)
git add backend/app.py
git add frontend/src/pages/Dashboard.jsx

# 3. Commit with description
git commit -m "feat: Add analytics dashboard"

# 4. Push to GitHub
git push
```

### Weekly: Update Documentation

```bash
# Update CHANGELOG.md with your changes
git add CHANGELOG.md
git commit -m "docs: Update changelog for week of Nov 3"
git push
```

---

## 🏷️ Using Tags for Versions

When you reach a significant milestone:

```bash
# Create a version tag
git tag -a v1.1.0 -m "Version 1.1.0: Added email integration"

# Push the tag to GitHub
git push origin v1.1.0

# Or push all tags
git push --tags
```

This creates a "Release" on GitHub that others can download.

---

## 🌿 Using Branches (Advanced)

For testing new features without affecting your main code:

```bash
# Create a new branch for a feature
git checkout -b feature/email-integration

# Make your changes and commit
git add .
git commit -m "feat: Add email sending functionality"

# Push the branch to GitHub
git push -u origin feature/email-integration

# When ready, merge back to main:
git checkout main
git merge feature/email-integration
git push
```

---

## 🔍 Useful Git Commands

### Check Status
```bash
git status              # See what files changed
git log --oneline       # See commit history
git diff                # See exact changes made
```

### Undo Changes
```bash
# Undo changes to a file (before commit)
git checkout -- filename.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) ⚠️
git reset --hard HEAD~1
```

### Pull Latest from GitHub
```bash
# If working from multiple computers
git pull
```

---

## 📦 .gitignore - What Gets Excluded

These files/folders are automatically excluded (already configured):

✅ **Excluded from GitHub:**
- `.env` - Your API keys (security!)
- `venv/` - Python virtual environment
- `node_modules/` - Node packages
- `database/*.db` - Your actual database
- `__pycache__/` - Python cache files
- `*.log` - Log files
- `.DS_Store` - Mac system files

✅ **Included on GitHub:**
- All source code (`.py`, `.jsx`, `.js`)
- Configuration files (`package.json`, `requirements.txt`)
- Documentation (`.md` files)
- Scripts (`launch.sh`, `stop.sh`)
- `env.example` - Template for environment variables

---

## 🔐 Security Checklist

Before pushing to GitHub, verify:

- [ ] `.env` file is in `.gitignore` ✅ (already done)
- [ ] No API keys in code ✅ (they're in .env)
- [ ] Database files excluded ✅ (already done)
- [ ] `env.example` exists for others ✅ (already created)

---

## 🚨 Emergency: Accidentally Committed Sensitive Data

If you accidentally committed your `.env` file with API keys:

```bash
# Remove the file from Git (but keep it locally)
git rm --cached .env

# Commit the removal
git commit -m "Remove .env from version control"

# Push to GitHub
git push

# Then: ROTATE your API key on OpenAI's website!
```

---

## 🎯 Quick Reference Card

```bash
# Daily workflow
git status           # What changed?
git add .           # Stage all changes
git commit -m "..."  # Save with message
git push            # Upload to GitHub

# When starting work (if using multiple computers)
git pull            # Download latest changes

# View history
git log --oneline   # See past commits
git diff            # See current changes
```

---

## 🌟 Making Your Repo Look Professional

### Add a LICENSE file

```bash
# Create a LICENSE file (MIT License example)
# GitHub can help you add one through the web interface:
# Repository → Add file → Create new file → Name it "LICENSE"
# GitHub will offer license templates
```

### Add Topics to Your Repo

On GitHub:
1. Go to your repository
2. Click the ⚙️ gear icon next to "About"
3. Add topics: `tutoring`, `ai`, `education`, `openai`, `flask`, `react`, `report-generator`

### Add a Screenshot

1. Take a screenshot of your app
2. Create an `images/` folder in your repo
3. Add the screenshot: `images/dashboard.png`
4. Reference it in README.md:
```markdown
![Sage Reports Dashboard](images/dashboard.png)
```

---

## 📊 Keeping Your Changelog Updated

After each significant update, add to `CHANGELOG.md`:

```markdown
## 🗓️ Session: [Date]

### Summary
Brief description of what changed

### Features Added
- Feature 1
- Feature 2

### Bug Fixes
- Fix 1
- Fix 2

### Files Modified
- `backend/app.py`
- `frontend/src/pages/Dashboard.jsx`
```

Then commit:
```bash
git add CHANGELOG.md
git commit -m "docs: Update changelog for [feature name]"
git push
```

---

## 🎓 Learning More

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

---

## 💡 Tips for Maintaining Your Repo

1. **Commit often** - Small, frequent commits are better than large ones
2. **Write clear messages** - Your future self will thank you
3. **Update docs** - Keep README and CHANGELOG current
4. **Tag releases** - Mark significant milestones
5. **Test before pushing** - Make sure your code works
6. **Use branches** - For experimental features
7. **Back up regularly** - GitHub is your backup

---

## ❓ Common Questions

**Q: How often should I push to GitHub?**
A: After each work session, or when you complete a logical chunk of work.

**Q: Can I delete files from GitHub?**
A: Yes, just delete locally, commit, and push:
```bash
rm filename
git add .
git commit -m "Remove unused file"
git push
```

**Q: How do I rename the repository?**
A: On GitHub: Settings → Repository name → Rename

**Q: What if I want to work on multiple computers?**
A: Use `git pull` before starting work and `git push` when done.

---

## 🎉 You're Ready!

Your Sage Reports codebase is now GitHub-ready with:
- ✅ Clean, organized file structure
- ✅ Professional README
- ✅ Proper .gitignore
- ✅ Documentation organized
- ✅ Git repository initialized
- ✅ Security best practices

Happy coding! 🚀

