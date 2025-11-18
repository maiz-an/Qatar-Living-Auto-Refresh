# Qatar Living Auto Refresh (QLAR)

A GitHub Actions workflow that automatically bumps your Qatar Living job posts to keep them at the top of the listings.

## 🚀 Features

- **Automatic Bumping**: Refreshes your job posts 3 times daily
- **Secure**: Uses GitHub Secrets to store cookies securely
- **Flexible**: Easy to set up for any Qatar Living account
- **Reliable**: Multiple retry mechanisms with fallbacks
- **Free**: Runs entirely on GitHub's free tier

## 📋 Prerequisites

- GitHub account
- Qatar Living account with active job posting
- Basic knowledge of copying/pasting text

## 🛠️ Setup Guide (5-10 minutes)

### Step 1: Fork this Repository

1. Click the "Fork" button at the top right of this repository
2. Create your own copy under your GitHub account

### Step 2: Get Your Qatar Living Cookies

1. **Login to Qatar Living** in your browser
   - Go to [https://www.qatarliving.com](https://www.qatarliving.com)
   - Login to your account

2. **Open Developer Tools**
   - Press `F12` or right-click → "Inspect Element"
   - Go to the "Console" tab

3. **Run the Cookie Extractor**
   - Copy and paste this code into the console:

   ```javascript
   var cookies = document.cookie.split(';');
   var cookieObj = {};
   cookies.forEach((cookie) => {
       var [name, value] = cookie.trim().split('=');
       cookieObj[name] = value || '';
   });
   console.log('Copy this JSON to GitHub Secrets:');
   console.log(JSON.stringify(cookieObj));
   copy(JSON.stringify(cookieObj));
   console.log('✅ JSON copied to clipboard!');
   ```

   - Press `Enter`

4. **Save the Cookies**
   - The JSON is automatically copied to your clipboard
   - Save it somewhere safe (like a text file) for the next step

### Step 3: Get Your Bump URL

1. **Go to Your Job Post**
   - Navigate to your job posting on Qatar Living
   - Look for the "Bump to top" button/link

2. **Copy the Bump URL**
   - Right-click on "Bump to top" → "Copy link address"
   - Or find it in the page source
   - The URL should look like:

     ```
     https://www.qatarliving.com/bump/node/12345678?destination=/jobseeker/yourusername/your-job-title
     ```

### Step 4: Set Up GitHub Secrets

1. **Go to Your Repository Settings**
   - In your forked repository, click "Settings"
   - On the left sidebar, click "Secrets and variables" → "Actions"

2. **Add QATAR_COOKIES Secret**
   - Click "New repository secret"
   - Name: `QATAR_COOKIES`
   - Value: Paste the JSON cookies you copied earlier
   - Click "Add secret"

3. **Add BUMP_URL Secret**
   - Click "New repository secret" again
   - Name: `BUMP_URL`
   - Value: Paste your bump URL
   - Click "Add secret"

### Step 5: Enable GitHub Actions

1. **Check Actions Permissions**
   - Go to Settings → Actions → General
   - Ensure "Allow all actions and reusable workflows" is selected
   - Scroll down and click "Save"

2. **Run the Workflow Manually (Test)**
   - Go to the "Actions" tab in your repository
   - Click "Qatar Living Auto Refresh" in the left sidebar
   - Click "Run workflow" → "Run workflow"
   - Wait for the workflow to complete (2-3 minutes)

## ⚙️ Configuration

### Schedule Timing

The workflow runs at:

- **7:30 AM Qatar Time** (4:30 AM UTC)
- **12:30 PM Qatar Time** (9:30 AM UTC)
- **3:30 PM Qatar Time** (12:30 PM UTC)

To modify the schedule, edit `.github/workflows/auto-refresh.yml`:

```yaml
schedule:
  - cron: '30 4,9,12 * * *'  # Change these times
```

### Manual Runs

You can manually trigger bumps anytime:

1. Go to Actions → Qatar Living Auto Refresh
2. Click "Run workflow"

## 🔧 Troubleshooting

### Common Issues

1. **"Authentication failed - cookies may be expired"**
   - Cookies expire after some time
   - Repeat Step 2 to get fresh cookies and update the secret

2. **"No bump URL found"**
   - Check your BUMP_URL secret is correctly set
   - Ensure the URL is in the correct format

3. **Workflow not running**
   - Check that Actions are enabled in repository settings
   - Verify the schedule syntax in the YAML file

4. **"Refresh failed"**
   - Qatar Living might have temporary issues
   - The workflow will retry automatically next run
   - Check the workflow logs for specific error messages

### Updating Cookies

Cookies typically last 1-4 weeks. When you see authentication errors:

1. Repeat Step 2 to get new cookies
2. Update the QATAR_COOKIES secret with the new JSON
3. The next run should work automatically

## 📁 File Structure

```
QLAR/
├── .github/
│   └── workflows/
│       └── auto-refresh.yml    # GitHub Actions workflow
├── refresh_post.py             # Main Python script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔒 Security Notes

- **Never share your cookies** - they provide full access to your Qatar Living account
- GitHub Secrets are encrypted and only accessible to repository owners
- The workflow runs in isolated environments that are destroyed after each run
- Review the code to ensure no sensitive data is logged

## ❓ Frequently Asked Questions

**Q: How often should I update the cookies?**
A: Typically every 2-4 weeks, or when you see authentication errors.

**Q: Can I use this for multiple job posts?**
A: Yes! You can:

- Duplicate the workflow file and create separate secrets for each job
- Or modify the script to handle multiple URLs

**Q: Will this get my account banned?**
A: This follows Qatar Living's bump limits (3 times daily), which should be within acceptable use.

**Q: Can I run this more than 3 times daily?**
A: Not recommended as it may violate Qatar Living's terms of service.

## 🆘 Support

If you encounter issues:

1. Check the workflow logs for error details
2. Ensure all setup steps were followed correctly
3. Verify your cookies and bump URL are current

## 📄 License

This project is for educational purposes. Use responsibly and in accordance with Qatar Living's terms of service.

---

**Happy job hunting! 🎉**
