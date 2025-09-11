# ⚡ Quick Start: Deploy TOXO Package in 5 Minutes

## 🎯 What You Need

1. **GitHub account** (free)
2. **PyPI account** (free) - https://pypi.org/account/register/
3. **5 minutes** of your time

## 🚀 Super Quick Deployment

### Step 1: Create GitHub Repository (2 minutes)

1. Go to https://github.com/new
2. Repository name: `toxo-python`
3. Description: `TOXO - No-Code LLM Training Platform Python Package`
4. Make it **Public** ✅
5. Click "Create repository"

### Step 2: Push Your Code (1 minute)

```bash
# Copy these commands exactly (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/toxo-python.git
git branch -M main
git push -u origin main
```

### Step 3: Create PyPI Account (1 minute)

1. Go to https://pypi.org/account/register/
2. Username: `toxotune` (or your choice)
3. Email: Your business email
4. Password: Strong password
5. Verify email

### Step 4: Deploy Package (1 minute)

```bash
# Install publishing tool
pip install twine

# Deploy to PyPI
python -m build
python -m twine upload dist/*
```

**Enter your PyPI username and password when prompted**

## 🎉 DONE! 

Your package is now live! Anyone can install it:

```bash
pip install toxo
```

## 📊 Test It Works

```python
from toxo import ToxoLayer
print("TOXO package installed successfully!")
```

## 🔄 For Future Updates

1. Update version in `setup.py` (line 12)
2. `git commit -m "v1.0.1: Bug fixes"`
3. `git push`
4. `python -m build && python -m twine upload dist/*`

## 🆘 Need Help?

- **Full Guide**: See `DEPLOYMENT_GUIDE.md`
- **Auto Deploy**: Run `./deploy.sh`
- **Support**: support@toxotune.com

---

**Total Time: 5 minutes** ⏱️

Your TOXO package will be publicly available! 🚀
