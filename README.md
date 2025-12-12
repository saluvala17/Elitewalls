# Elite Wall Systems - Job Costing App (Google Sheets Version)

A simple job costing application that uses Google Sheets as the database.

## Features

- **Job Management** - Create and track construction jobs
- **Weekly Cost Entry** - Enter costs by category (Insurance, Labor, Materials, etc.)
- **Customer & Vendor Management** - Track GCs and suppliers
- **Dashboard** - Visual overview with charts
- **Reports** - Generate and export to Excel

## Why Google Sheets?

- ✅ **Free** - No database costs
- ✅ **Familiar** - Your team already knows spreadsheets
- ✅ **Accessible** - View data directly in Google Sheets anytime
- ✅ **Backup** - Google handles backups automatically
- ✅ **Simple** - No database administration needed

---

## Quick Setup (MacBook)

### Step 1: Install Python

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Verify
python3 --version
```

### Step 2: Download & Setup Project

```bash
# Create folder and extract files
cd ~
mkdir elite-wall-sheets
cd elite-wall-sheets
# Extract the zip file here

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Create Google Cloud Project (One-time Setup)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it: `elite-wall-systems` → Create
4. Wait for project to create, then select it

### Step 4: Enable Google Sheets API

1. Go to [APIs & Services](https://console.cloud.google.com/apis/library)
2. Search for "Google Sheets API"
3. Click on it → Click "Enable"
4. Also search for "Google Drive API" and enable it

### Step 5: Create Service Account

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "Service Account"
3. Name: `elite-wall-app`
4. Click "Create and Continue" → "Done"
5. Click on the service account you just created
6. Go to "Keys" tab → "Add Key" → "Create new key"
7. Select "JSON" → "Create"
8. **Save the downloaded file as `credentials.json` in your project folder**

### Step 6: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new blank spreadsheet
3. Name it: `Elite Wall Systems - Job Costing`
4. **Copy the Spreadsheet ID from the URL:**
   ```
   https://docs.google.com/spreadsheets/d/[THIS-IS-YOUR-SPREADSHEET-ID]/edit
   ```

### Step 7: Share Sheet with Service Account

1. Open your `credentials.json` file
2. Find the `client_email` field (looks like: `elite-wall-app@xxx.iam.gserviceaccount.com`)
3. In Google Sheets, click "Share"
4. Paste the service account email
5. Give it "Editor" access
6. Click "Share"

### Step 8: Configure the App

Create a file called `.streamlit/secrets.toml`:

```bash
mkdir -p .streamlit
nano .streamlit/secrets.toml
```

Add this content:
```toml
SPREADSHEET_ID = "your-spreadsheet-id-here"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "elite-wall-app@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

**OR** simply put your `credentials.json` file in the project root folder.

### Step 9: Run the App

```bash
# Make sure virtual environment is active
source venv/bin/activate

# Run Streamlit
streamlit run Home.py
```

The app will open at `http://localhost:8501`

### Step 10: Initialize Sheets

1. When the app opens, click "🔄 Initialize Sheets" in the sidebar
2. This creates the required tabs in your Google Sheet

---

## Project Structure

```
elite-wall-sheets/
├── .streamlit/
│   ├── config.toml         # Streamlit theme
│   └── secrets.toml        # Your credentials (create this)
├── src/
│   ├── google_sheets.py    # Google Sheets database
│   └── utils.py            # Helper functions
├── pages/
│   ├── 1_Dashboard.py      # Visual dashboard
│   ├── 2_Jobs.py           # Job management
│   ├── 3_Cost_Entry.py     # Weekly costs
│   ├── 4_Customers.py      # GC management
│   ├── 5_Vendors.py        # Vendor management
│   └── 6_Reports.py        # Reports
├── Home.py                 # Main page
├── credentials.json        # Google credentials (create this)
├── requirements.txt        # Dependencies
└── README.md              # This file
```

---

## Google Sheet Structure

The app creates these tabs automatically:

| Tab | Purpose |
|-----|---------|
| **Customers** | General Contractors (GCs) |
| **Vendors** | Suppliers, subcontractors |
| **Jobs** | All jobs with budgets |
| **WeeklyCosts** | Weekly cost entries |

You can view/edit data directly in Google Sheets!

---

## Troubleshooting

### "Could not connect to Google Sheets"
- Check `credentials.json` is in project folder
- Verify SPREADSHEET_ID is correct
- Make sure sheet is shared with service account email

### "Permission denied"
- Share the Google Sheet with the service account email (Editor access)
- Check the service account email in `credentials.json` → `client_email`

### "Module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### App is slow
- Google Sheets API has rate limits
- The app caches data to minimize API calls
- For large datasets (100+ jobs), consider upgrading to Supabase

---

## Costs

| Item | Cost |
|------|------|
| Google Sheets | **Free** |
| Google Cloud (API) | **Free** (generous limits) |
| Streamlit (local) | **Free** |
| Streamlit Cloud | **Free** (public apps) |

**Total: $0/month**

---

## Support

For questions:
1. Check Troubleshooting section above
2. Google Sheets API docs: https://developers.google.com/sheets/api
3. Streamlit docs: https://docs.streamlit.io

---

Built for Elite Wall Systems 🏗️
