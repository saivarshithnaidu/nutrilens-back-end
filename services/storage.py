import os
from datetime import datetime
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase Client Setup
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

BUCKET_NAME = "images"

class StorageService:
    @staticmethod
    def upload_image(file_obj, user_id: int) -> str:
        """
        Uploads file to Supabase Storage and returns the path/key.
        Format: {user_id}/{timestamp}_{uuid}.jpg
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        filename = f"{timestamp}_{unique_id}.jpg"
        file_path = f"{user_id}/{filename}"
        
        # Read file bytes
        file_content = file_obj.read()
        
        # Upload to Supabase
        # 'file_content' should be bytes. content_type is optional but goodpractice.
        supabase.storage.from_(BUCKET_NAME).upload(
            file_path, 
            file_content, 
            {"content-type": "image/jpeg"}
        )
            
        return file_path

    @staticmethod
    def get_image_path(key: str) -> str:
        """
        Get public URL or signed URL for the image.
        For internal processing, we might need to download it back 
        OR if we just need bytes, we download it.
        """
        # For Inference, we usually need the bytes.
        # But our analyze.py expects a file path to 'open'.
        # Since we are cloud-native now, we should download to a temp file
        # or change analyze.py to accept bytes (which we did partially in previous steps ?)
        
        # Let's download to a temp file to maintain compatibility with 'open(image_path)'
        # OR better: The upload_image in analyze.py passes 'file.file' which is a SpooledTemporaryFile.
        # If we uploaded it, we still have the original 'file' object in memory in the route handler!
        # BUT, the analyze route code calls `StorageService.upload_image` then `StorageService.get_image_path`.
        
        # We need a way to get the file content back for the 'open()' call in analyze.py
        # Actually, let's just cheat for the 'processing' part:
        # In analyze.py we have:
        # 1. upload_image(file.file, ...)
        # 2. get_image_path(...)
        # 3. open(image_path, "rb")
        
        # With S3/Supabase, we can't 'open' a remote URL. 
        # We should probably download it to a temp path.
        
        import tempfile
        
        # Download file
        response = supabase.storage.from_(BUCKET_NAME).download(key)
        
        # Write to temp file
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp.write(response)
        temp.close()
        
        return temp.name

    @staticmethod
    def delete_image(key: str):
        try:
            # Delete local temp file if it was downloaded? 
            # The key passed here is the Supabase key.
            # But we also created a temp file in get_image_path. 
            # We should clean that up too if possible, but the interface takes 'key'.
            
            # 1. Delete from Supabase
            supabase.storage.from_(BUCKET_NAME).remove([key])
            
            # 2. To strictly clean up the temp file we created in get_image_path, 
            # we would need the temp path. Mock implementation returned a path.
            # Supabase impl is trickier.
            # We'll rely on OS cleaning up temp files for now or improve analyze.py
        except Exception as e:
            print(f"Error deleting image: {e}")
