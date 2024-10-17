from firebase_admin import credentials, storage
from django.utils import timezone
from django.conf import settings
from services.utils import read_json
import firebase_admin


cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred, {'storageBucket': settings.FIREBASE_BUCKET_NAME})
bucket = storage.bucket()

def init_firebase():
    dir_firebase = ['css', 'js', 'web-ico', 'image-assets', 'image-assets/banner']
    print('initializing Firebase Storage. . .')
    for dir in dir_firebase:
      blob_list = bucket.list_blobs(prefix=f'{dir}')
      for blob in blob_list:
          blob.make_public()
    print('firebase ready.')
        

def get_image(path):
    url = bucket.blob(path)
    return url


def firebase_upload(path, ref_file, filename, ct):
    now = timezone.now()
    try:
      formatted_name = filename.replace(' ', '-').lower()
      folder_path = f"yummypiv/{path}/{now.strftime('%m-%Y')}-{formatted_name}.{ct}"
      bucket = storage.bucket()
      blob = bucket.blob(folder_path)
      blob.upload_from_file(ref_file, content_type=f'image/{ct}')
      # Buat URL publik
      blob.make_public()
      public_url = blob.public_url
      # save local info
      return (True, public_url)
    except Exception as err:
      print(err)
      return (False, 'Terjadi kesalahan saat upload, silahka ulangi.')
    
    
def firebase_delete(url):
  
    filepath = url.replace(f'https://storage.googleapis.com/{settings.FIREBASE_BUCKET_NAME}/', '')

    # Referensi ke file yang akan dihapus
    blob = bucket.blob(filepath)
    
    try:        
        blob.delete()
        return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False
