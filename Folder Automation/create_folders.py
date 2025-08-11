import json
import sys
import os
from typing import Optional, Dict, Any
from googleapiclient.discovery import build
from google.oauth2 import service_account

class FolderCreator:
    def __init__(self, service_account_json: str, config_path: str = "config.json"):
        """Initialize the FolderCreator with service account credentials"""
        self.config = self._load_config(config_path)
        self.service = self._authenticate(service_account_json)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Config file {config_path} not found")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON in config file: {e}")
    
    def _authenticate(self, service_account_json: str) -> Any:
        """Authenticate with Google Drive API using service account"""
        try:
            credentials_info = json.loads(service_account_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            raise Exception(f"Authentication failed: {e}")
    
    def create_folder(self, name: str, parent_id: str) -> str:
        """Create a new folder in Google Drive"""
        folder_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        
        try:
            folder = self.service.files().create(body=folder_metadata, fields='id').execute()
            return folder.get('id')
        except Exception as e:
            raise Exception(f"Failed to create folder '{name}': {e}")
    
    def copy_file(self, file_id: str, new_name: str, parent_id: str) -> str:
        """Copy a file to a new location with a new name"""
        copy_metadata = {
            'name': new_name,
            'parents': [parent_id]
        }
        
        try:
            copied_file = self.service.files().copy(
                fileId=file_id, 
                body=copy_metadata,
                fields='id'
            ).execute()
            return copied_file.get('id')
        except Exception as e:
            raise Exception(f"Failed to copy file '{new_name}': {e}")
    
    def list_folder_contents(self, folder_id: str) -> tuple:
        """List all files and folders in a given folder"""
        try:
            # Get all items in the folder
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields='files(id, name, mimeType)'
            ).execute()
            
            files = []
            folders = []
            
            for item in results.get('files', []):
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    folders.append(item)
                else:
                    files.append(item)
            
            return files, folders
        except Exception as e:
            raise Exception(f"Failed to list folder contents: {e}")
    
    def copy_folder_contents(self, source_folder_id: str, destination_folder_id: str, company_name: str):
        """Recursively copy folder contents from source to destination"""
        files, folders = self.list_folder_contents(source_folder_id)
        
        # Copy all files
        for file_item in files:
            file_name = file_item['name']
            file_id = file_item['id']
            
            # Special handling for Authorized User List
            if file_name == self.config['folder_structure']['user_list_original_name']:
                new_name = f"{company_name}{self.config['folder_structure']['user_list_suffix']}"
            else:
                new_name = file_name
            
            print(f"Copying file: {file_name} -> {new_name}")
            self.copy_file(file_id, new_name, destination_folder_id)
        
        # Copy all subfolders recursively
        for folder_item in folders:
            folder_name = folder_item['name']
            folder_id = folder_item['id']
            
            print(f"Creating subfolder: {folder_name}")
            new_subfolder_id = self.create_folder(folder_name, destination_folder_id)
            
            # Recursively copy contents
            self.copy_folder_contents(folder_id, new_subfolder_id, company_name)
    
    def create_client_folder_structure(self, organization_name: str) -> Dict[str, str]:
        """Create the complete client folder structure"""
        try:
            # Create main client folder
            main_folder_name = f"{organization_name}{self.config['folder_structure']['main_folder_suffix']}"
            print(f"Creating main folder: {main_folder_name}")
            
            destination_folder_id = self.config['google_drive']['destination_folder_id']
            template_folder_id = self.config['google_drive']['template_folder_id']
            
            main_folder_id = self.create_folder(main_folder_name, destination_folder_id)
            
            # Copy template folder contents
            print("Copying template folder structure...")
            self.copy_folder_contents(template_folder_id, main_folder_id, organization_name)
            
            # Get the folder URL for return
            folder_url = f"https://drive.google.com/drive/folders/{main_folder_id}"
            
            return {
                'success': True,
                'folder_id': main_folder_id,
                'folder_name': main_folder_name,
                'folder_url': folder_url,
                'message': f"Successfully created folder structure for {organization_name}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to create folder structure for {organization_name}"
            }

def main():
    """Main function to run folder creation"""
    if len(sys.argv) != 2:
        print("Usage: python create_folders.py <organization_name>")
        sys.exit(1)
    
    organization_name = sys.argv[1]
    
    # Get service account JSON from environment variable
    service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not service_account_json:
        print("Error: GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set")
        sys.exit(1)
    
    try:
        # Create folder creator instance
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        creator = FolderCreator(service_account_json, config_path)
        
        # Create folder structure
        result = creator.create_client_folder_structure(organization_name)
        
        # Output result as JSON for GitHub Action
        print(json.dumps(result, indent=2))
        
        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'message': f"Script execution failed: {e}"
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
