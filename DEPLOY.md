# Deployment Guide

## Deploy to Vercel

### Prerequisites
1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

### Deploy Steps

1. **From your project directory**, run:
```bash
cd /Users/ronkommoji/Desktop/DevotionalAPI
vercel
```

2. **Follow the prompts:**
   - Set up and deploy? **Y**
   - Which scope? (Select your account)
   - Link to existing project? **N** (for first deployment)
   - Project name? (Press Enter for default or enter a name)
   - Directory? (Press Enter for current directory)
   - Override settings? **N**

3. **For production deployment:**
```bash
vercel --prod
```

### Alternative: Deploy via GitHub

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your GitHub repository
5. Vercel will auto-detect Python and deploy

### Troubleshooting Vercel

If you encounter issues with Vercel's Python support, you may need to add Mangum adapter:

1. Add to `requirements.txt`:
```
mangum==0.17.0
```

2. Update `api/index.py`:
```python
from mangum import Mangum
from api.main import app

handler = Mangum(app)
```

---

## Alternative: Deploy to Railway

Railway has excellent Python support:

1. **Install Railway CLI:**
```bash
npm i -g @railway/cli
```

2. **Login:**
```bash
railway login
```

3. **Initialize and deploy:**
```bash
railway init
railway up
```

4. **Set start command:**
```bash
railway variables set START_COMMAND="uvicorn api.main:app --host 0.0.0.0 --port $PORT"
```

---

## Alternative: Deploy to Render

1. Go to [render.com](https://render.com)
2. Create a new "Web Service"
3. Connect your GitHub repository
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3

---

## Environment Variables

If needed, you can set environment variables:
- **Vercel:** `vercel env add VARIABLE_NAME`
- **Railway:** `railway variables set VARIABLE_NAME=value`
- **Render:** Dashboard → Environment → Add Environment Variable

---

## Post-Deployment

After deployment, you'll get a URL like:
- Vercel: `https://your-project.vercel.app`
- Railway: `https://your-project.up.railway.app`
- Render: `https://your-project.onrender.com`

Test your endpoints:
- `https://your-url/today`
- `https://your-url/docs` (FastAPI interactive docs)
