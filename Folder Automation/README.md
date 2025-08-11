To get a folder ID from Google Drive:
1. Open the folder in Google Drive
2. The ID is in the URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
3. Copy the ID part after `/folders/`

## Usage

### Creating a New Client Folder

1. **Go to Issues** in your GitHub repository
2. **Click "New issue"**
3. **Select "Client Folder Creation"** template
4. **Enter the organization name** in the form
5. **Submit the issue**

The automation will:
- Process the request automatically
- Create the folder structure in Google Drive
- Comment on the issue with results
- Close the issue when complete

### Folder Structure Created

```
[Organization Name] (L2)/
├── [Template folder contents copied recursively]
├── Shared with Client/
│   ├── [Template subfolders]
│   └── [Organization Name] Authorized User List
└── User Agreements/
```

## Configuration

### config.json

```json
{
  "google_drive": {
    "template_folder_id": "YOUR_TEMPLATE_FOLDER_ID",
    "destination_folder_id": "YOUR_DESTINATION_FOLDER_ID"
  },
  "folder_structure": {
    "main_folder_suffix": " (L2)",
    "shared_folder_name": "Shared with Client",
    "user_list_original_name": "Authorized User List",
    "user_list_suffix": " Authorized User List"
  }
}
```

### Required Repository Secrets

- `GOOGLE_SERVICE_ACCOUNT_JSON`: Complete JSON content of your service account key

## Troubleshooting

### Common Issues

1. **"Authentication failed"**
   - Verify the `GOOGLE_SERVICE_ACCOUNT_JSON` secret is correctly set
   - Ensure the JSON is valid and complete

2. **"Permission denied"**
   - Check that the service account has "Editor" access to both template and destination folders
   - Verify the folder IDs are correct in `config.json`

3. **"Template folder not found"**
   - Ensure the template folder ID in `config.json` is correct
   - Verify the service account can access the template folder

4. **"Organization name not found"**
   - Ensure you're using the correct issue template
   - Check that the organization name field is filled out

### Viewing Logs

1. Go to **Actions** tab in your GitHub repository
2. Click on the failed workflow run
3. Expand the **"Create folder structure"** step to see detailed logs

## File Structure

```
Folder Automation/
├── config.json              # Configuration settings
├── create_folders.py        # Main Python script
├── requirements.txt         # Python dependencies
└── README.md               # This documentation

.github/
├── ISSUE_TEMPLATE/
│   └── folder_creation.yml  # Issue form template
└── workflows/
    └── folder-creation.yml  # GitHub Action workflow
```

## Development

### Testing Locally

1. Install dependencies:
   ```bash
   cd "Folder Automation"
   pip install -r requirements.txt
   ```

2. Set environment variable:
   ```bash
   export GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'
   ```

3. Run the script:
   ```bash
   python create_folders.py "Test Organization"
   ```

### Modifying the Folder Structure

To change the folder naming or structure:
1. Update the relevant settings in `config.json`
2. Modify the logic in `create_folders.py` if needed
3. Test with a new organization name

## Security Notes

- Service account credentials are stored securely as GitHub repository secrets
- The service account only has access to the specific Google Drive folders you share
- No sensitive data is logged in the GitHub Action outputs

