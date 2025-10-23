# Gmail Tools

A simple, declarative command-line tool for programmatic Gmail control. Perfect for job searching, email management, and automation.

## Features

- **OAuth2 Authentication**: Secure Gmail API access
- **List Emails**: View recent emails from your inbox
- **Keyword Filtering**: Filter emails by keywords in subject or body
- **Export to EML**: Download emails as .eml files for archival
- **Export to HTML**: Generate a single HTML file with all emails, preserving formatting and links
- **Gmail Query Support**: Use Gmail's powerful search syntax for pre-filtering

## Installation

### 1. Clone or download this repository

```bash
cd gmail-tools
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Google Cloud OAuth2 credentials

You can authenticate using either environment variables (recommended) or a credentials file.

#### Option A: Using Environment Variables (Recommended)

Set these environment variables in your shell:

```bash
export GOOGLE_OAUTH2_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_OAUTH2_CLIENT_SECRET="your-client-secret"
```

To make these permanent, add them to your `~/.zshrc` or `~/.bashrc` file.

#### Option B: Using credentials.json file

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth2 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Name it (e.g., "Gmail Tools")
   - Download the credentials JSON file
5. Save the downloaded file as `credentials.json` in the gmail-tools directory

### 4. First-time authentication

The first time you run any command, a browser window will open asking you to authenticate:

```bash
python cli.py list-emails
```

After authentication, a `token.json` file will be created for future use.

## Usage

### List recent emails

```bash
# List 10 most recent emails
python cli.py list-emails

# List 25 most recent emails
python cli.py list-emails -n 25

# List emails with Gmail query
python cli.py list-emails -q "from:recruiter@company.com"
```

### Filter emails by keywords

```bash
# Filter by single keyword
python cli.py filter-emails -k "interview"

# Filter by multiple keywords (OR logic)
python cli.py filter-emails -k "interview" -k "onsite" -k "phone screen"

# Search subject only
python cli.py filter-emails -k "interview" --subject-only

# Search body only
python cli.py filter-emails -k "interview" --body-only

# Case-sensitive search
python cli.py filter-emails -k "Python" --case-sensitive

# Fetch more emails before filtering
python cli.py filter-emails -k "interview" -n 100
```

### Export filtered emails

```bash
# Export matching emails to EML files
python cli.py filter-emails -k "interview" --eml

# Export to specific directory
python cli.py filter-emails -k "interview" --eml -o my_emails

# Export to HTML file
python cli.py filter-emails -k "interview" -h interviews.html

# Export to both EML and HTML
python cli.py filter-emails -k "interview" --eml -h interviews.html
```

### Export all recent emails

```bash
# Export to EML files
python cli.py export-eml -n 50 -o downloads

# Export to HTML
python cli.py export-html -n 50 -o emails.html

# Use Gmail query for pre-filtering
python cli.py export-html -q "is:unread from:recruiter" -o unread_from_recruiters.html
```

## Gmail Query Syntax

You can use Gmail's search operators with the `-q` option:

```bash
# Emails from specific sender
python cli.py list-emails -q "from:someone@example.com"

# Unread emails with subject
python cli.py filter-emails -q "is:unread subject:interview" -k "onsite"

# Emails within date range
python cli.py export-html -q "after:2024/01/01 before:2024/12/31"

# Emails with attachments
python cli.py list-emails -q "has:attachment"

# Combine multiple operators
python cli.py filter-emails -q "from:recruiter is:unread" -k "position"
```

[Gmail search operators reference](https://support.google.com/mail/answer/7190?hl=en)

## Common Use Cases for Job Searching

### Find all interview-related emails

```bash
python cli.py filter-emails -k "interview" -k "phone screen" -k "onsite" \
  -n 100 --eml -h interview_emails.html
```

### Export all recruiter emails from the last month

```bash
python cli.py export-html -q "from:recruiter after:$(date -v-1m +%Y/%m/%d)" \
  -o recruiter_emails.html
```

### Filter unread emails about specific positions

```bash
python cli.py filter-emails -q "is:unread" -k "Software Engineer" -k "Senior Developer" \
  -h new_positions.html
```

### Archive all job application confirmations

```bash
python cli.py filter-emails -k "application received" -k "thank you for applying" \
  --eml -o job_applications
```

## Project Structure

```
gmail-tools/
├── auth.py           # OAuth2 authentication
├── gmail_client.py   # Gmail API wrapper
├── filters.py        # Email filtering logic
├── exporters.py      # EML and HTML export
├── cli.py            # Command-line interface
├── requirements.txt  # Python dependencies
├── credentials.json  # OAuth2 credentials (you provide)
├── token.json        # Auth token (auto-generated)
└── README.md         # This file
```

## Tips

1. **First run**: The first time you authenticate, make sure you're logged into the correct Gmail account in your browser
2. **Token expiry**: If you get authentication errors, delete `token.json` and re-authenticate
3. **Large exports**: For exporting many emails, increase `-n` parameter (e.g., `-n 500`)
4. **HTML viewing**: Open the generated HTML files in any web browser to view your emails with full formatting
5. **EML files**: .eml files can be opened in most email clients (Thunderbird, Apple Mail, Outlook)

## Security Notes

- `credentials.json` and `token.json` contain sensitive data - never commit them to version control
- The tool only requests read-only Gmail access (`gmail.readonly` scope)
- All authentication is handled through Google's official OAuth2 flow
- Tokens are stored locally and never transmitted to third parties

## Troubleshooting

### "credentials.json not found"
Download OAuth2 credentials from Google Cloud Console (see Installation step 3)

### "Access blocked: This app's request is invalid"
Make sure you've enabled the Gmail API in Google Cloud Console

### "No messages found"
Try increasing the `-n` parameter or check your Gmail query syntax

### Authentication browser doesn't open
The authentication URL will be printed in the terminal - copy and paste it into your browser manually

## License

This project is provided as-is for personal use.
