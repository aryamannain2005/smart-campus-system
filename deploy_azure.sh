#!/bin/bash

# Azure Deployment Script for Smart Campus System
# Run this script after installing Azure CLI and logging in

set -e

# Configuration - CHANGE THESE VALUES
APP_NAME="smart-campus-lpu"           # Change if taken
RESOURCE_GROUP="smart-campus-rg"
LOCATION="eastus"
DB_NAME="smart-campus-db"
DB_ADMIN="campusadmin"
DB_PASSWORD="YourSecurePassword123!"   # CHANGE THIS!
GITHUB_REPO="https://github.com/aryamannain2005/smart-campus-system"

echo "🚀 Starting Azure Deployment for Smart Campus System"
echo "=================================================="

# Check if logged in
echo "📋 Checking Azure login status..."
az account show > /dev/null 2>&1 || {
    echo "❌ Not logged in to Azure. Running 'az login'..."
    az login
}

echo "✅ Logged in to Azure"

# Create Resource Group
echo ""
echo "📦 Creating Resource Group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION --output none
echo "✅ Resource Group created"

# Create App Service Plan
echo ""
echo "📋 Creating App Service Plan..."
az appservice plan create \
    --name "${APP_NAME}-plan" \
    --resource-group $RESOURCE_GROUP \
    --sku B1 \
    --is-linux \
    --output none
echo "✅ App Service Plan created"

# Create Web App
echo ""
echo "🌐 Creating Web App: $APP_NAME"
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan "${APP_NAME}-plan" \
    --runtime "PYTHON:3.11" \
    --output none
echo "✅ Web App created"

# Create PostgreSQL Server
echo ""
echo "🗄️ Creating PostgreSQL Database (this takes 2-3 minutes)..."
az postgres flexible-server create \
    --name $DB_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --admin-user $DB_ADMIN \
    --admin-password $DB_PASSWORD \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 15 \
    --yes \
    --output none
echo "✅ PostgreSQL Server created"

# Create Database
echo ""
echo "📊 Creating Database..."
az postgres flexible-server db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $DB_NAME \
    --database-name smartcampus \
    --output none
echo "✅ Database created"

# Allow Azure Services
echo ""
echo "🔓 Configuring firewall rules..."
az postgres flexible-server firewall-rule create \
    --resource-group $RESOURCE_GROUP \
    --name $DB_NAME \
    --rule-name AllowAzure \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0 \
    --output none
echo "✅ Firewall configured"

# Generate secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

# Configure App Settings
echo ""
echo "⚙️ Configuring application settings..."
DATABASE_URL="postgres://${DB_ADMIN}:${DB_PASSWORD}@${DB_NAME}.postgres.database.azure.com:5432/smartcampus?sslmode=require"

az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
    DJANGO_SECRET_KEY="$SECRET_KEY" \
    DEBUG="False" \
    ALLOWED_HOSTS="${APP_NAME}.azurewebsites.net" \
    DATABASE_URL="$DATABASE_URL" \
    CSRF_TRUSTED_ORIGINS="https://${APP_NAME}.azurewebsites.net" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    WEBSITE_PYTHON_VERSION="3.11" \
    --output none
echo "✅ App settings configured"

# Configure startup command
echo ""
echo "🔧 Configuring startup command..."
az webapp config set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file "gunicorn smart_campus.wsgi:application --bind 0.0.0.0:8000" \
    --output none
echo "✅ Startup command set"

# Deploy from GitHub
echo ""
echo "🔗 Connecting to GitHub repository..."
az webapp deployment source config \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --repo-url $GITHUB_REPO \
    --branch main \
    --manual-integration \
    --output none
echo "✅ GitHub connected"

# Trigger deployment
echo ""
echo "🚀 Deploying application..."
az webapp deployment source sync \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --output none
echo "✅ Deployment triggered"

echo ""
echo "=================================================="
echo "🎉 DEPLOYMENT COMPLETE!"
echo "=================================================="
echo ""
echo "Your app URL: https://${APP_NAME}.azurewebsites.net"
echo ""
echo "⚠️  NEXT STEPS:"
echo "1. Wait 2-3 minutes for deployment to complete"
echo "2. Run database migrations:"
echo "   az webapp ssh --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo "   Then run: python manage.py migrate && python manage.py collectstatic --noinput"
echo ""
echo "3. Create admin user:"
echo "   python manage.py createsuperuser"
echo ""
echo "📋 View logs: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
