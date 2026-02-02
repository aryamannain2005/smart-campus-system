# Azure Deployment Guide for Smart Campus System

## Step 1: Get Azure for Students (FREE)

1. Go to: **https://azure.microsoft.com/free/students**
2. Click **"Start Free"**
3. Sign in with your **university email** (e.g., `@lpu.in`)
4. Verify your student status
5. Get **$100 free credits** - no credit card needed!

---

## Step 2: Install Azure CLI

### On macOS:
```bash
brew install azure-cli
```

### On Windows:
Download from: https://aka.ms/installazurecliwindows

### Verify installation:
```bash
az --version
```

---

## Step 3: Login to Azure

```bash
az login
```

This opens a browser - sign in with your university account.

---

## Step 4: Create Resources (One-time setup)

Run these commands in order:

### 4.1 Create Resource Group
```bash
az group create --name smart-campus-rg --location eastus
```

### 4.2 Create App Service Plan (Free tier)
```bash
az appservice plan create \
    --name smart-campus-plan \
    --resource-group smart-campus-rg \
    --sku B1 \
    --is-linux
```

### 4.3 Create Web App
```bash
az webapp create \
    --name smart-campus-lpu \
    --resource-group smart-campus-rg \
    --plan smart-campus-plan \
    --runtime "PYTHON:3.11"
```

> **Note:** If `smart-campus-lpu` is taken, try `smart-campus-YOUR-STUDENT-ID`

### 4.4 Create PostgreSQL Database (Free tier)
```bash
az postgres flexible-server create \
    --name smart-campus-db \
    --resource-group smart-campus-rg \
    --location eastus \
    --admin-user campusadmin \
    --admin-password YourSecurePassword123! \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 15
```

### 4.5 Create Database
```bash
az postgres flexible-server db create \
    --resource-group smart-campus-rg \
    --server-name smart-campus-db \
    --database-name smartcampus
```

### 4.6 Allow Azure Services to Connect
```bash
az postgres flexible-server firewall-rule create \
    --resource-group smart-campus-rg \
    --name smart-campus-db \
    --rule-name AllowAzure \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0
```

---

## Step 5: Configure App Settings

```bash
az webapp config appsettings set \
    --name smart-campus-lpu \
    --resource-group smart-campus-rg \
    --settings \
    DJANGO_SECRET_KEY="your-super-secret-key-change-this-to-random-50-chars" \
    DEBUG="False" \
    ALLOWED_HOSTS="smart-campus-lpu.azurewebsites.net" \
    DATABASE_URL="postgres://campusadmin:YourSecurePassword123!@smart-campus-db.postgres.database.azure.com:5432/smartcampus?sslmode=require" \
    CSRF_TRUSTED_ORIGINS="https://smart-campus-lpu.azurewebsites.net" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    WEBSITE_PYTHON_VERSION="3.11"
```

---

## Step 6: Deploy from GitHub

### 6.1 Configure Deployment Source
```bash
az webapp deployment source config \
    --name smart-campus-lpu \
    --resource-group smart-campus-rg \
    --repo-url https://github.com/aryamannain2005/smart-campus-system \
    --branch main \
    --manual-integration
```

### 6.2 Trigger Deployment
```bash
az webapp deployment source sync \
    --name smart-campus-lpu \
    --resource-group smart-campus-rg
```

---

## Step 7: Run Database Migrations

```bash
az webapp ssh --name smart-campus-lpu --resource-group smart-campus-rg
```

Once connected via SSH:
```bash
cd /home/site/wwwroot
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---

## Step 8: Access Your App!

Your app is now live at:
**https://smart-campus-lpu.azurewebsites.net**

---

## Quick Commands Reference

| Action | Command |
|--------|---------|
| View logs | `az webapp log tail --name smart-campus-lpu --resource-group smart-campus-rg` |
| Restart app | `az webapp restart --name smart-campus-lpu --resource-group smart-campus-rg` |
| Stop app | `az webapp stop --name smart-campus-lpu --resource-group smart-campus-rg` |
| Start app | `az webapp start --name smart-campus-lpu --resource-group smart-campus-rg` |
| Redeploy | `az webapp deployment source sync --name smart-campus-lpu --resource-group smart-campus-rg` |

---

## Troubleshooting

### App not starting?
```bash
az webapp log tail --name smart-campus-lpu --resource-group smart-campus-rg
```

### Database connection issues?
- Check firewall rules allow Azure services
- Verify DATABASE_URL has `?sslmode=require`

### Static files not loading?
```bash
az webapp ssh --name smart-campus-lpu --resource-group smart-campus-rg
python manage.py collectstatic --noinput
```

---

## Cost Estimate (Free Tier)

| Resource | Monthly Cost |
|----------|-------------|
| App Service (B1) | Free with $100 credit |
| PostgreSQL (B1ms) | ~$15/month from credit |
| Storage | Minimal |
| **Total** | **~$15-20/month from free credit** |

Your $100 credit = **~5-6 months free hosting!**

---

## Alternative: Use Azure Portal (GUI)

If you prefer clicking instead of commands:

1. Go to **portal.azure.com**
2. Click **"Create a resource"**
3. Search **"Web App + Database"**
4. Fill in the details and deploy!

