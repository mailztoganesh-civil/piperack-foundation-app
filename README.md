# 🏗️ Modularized Piperack Foundation Design App

Interactive Streamlit app for **isolated footing + pedestal** design (stability + simplified ACI 318 reinforcement).

Inspired by real project calculation notes (SARB Field Development – AD204-601-G-03378).

---

## 🚀 Deploy to Streamlit Community Cloud (Free) – Best for iPad

### Step-by-step (you can do this entirely from iPad Safari)

1. **Create a free GitHub account** (if you don’t have one)  
   → https://github.com

2. **Create a new repository**
   - Tap the **+** → **New repository**
   - Repository name: `piperack-foundation-app` (or any name)
   - Set to **Public**
   - Tap **Create repository**

3. **Upload the files**
   - On the new empty repo page, tap **uploading an existing file**
   - Upload these files/folders:
     - `app.py`
     - `requirements.txt`
     - the whole `.streamlit` folder
   - Tap **Commit changes**

4. **Deploy on Streamlit Cloud**
   - Go to → https://share.streamlit.io
   - Sign in with the **same GitHub account**
   - Tap **New app**
   - Choose your repository
   - Main file path: `app.py`
   - Tap **Deploy!**

5. Wait 1–2 minutes.  
   You will get a public link like:  
   `https://piperack-foundation-app-xxxxx.streamlit.app`

6. Open that link in Safari on your iPad — done!

---

## Files included

- `app.py` → main application
- `requirements.txt` → Python packages
- `.streamlit/config.toml` → nice theme + settings

---

## Local run (on a computer)

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

**Disclaimer**: This is a prototype for learning and demonstration. Always have results checked by a qualified structural engineer.
