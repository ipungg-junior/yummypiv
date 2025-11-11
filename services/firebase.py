from firebase_admin import credentials, storage
from django.utils import timezone
from django.conf import settings
from services.utils import INFO_TAG, INSPECTOR, ERROR_TAG, convert_compress_image
import firebase_admin, time

try:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred, {'storageBucket': settings.FIREBASE_BUCKET_NAME})
    bucket = storage.bucket()
except Exception as firebase_error:
    ERROR_TAG('Firebase init, please check your credentials on your env')
    INSPECTOR(firebase_error)
    time.sleep(10)

def init_firebase():
    dir_firebase = ['static', 'media', 'media/product', 'media/testimonial', 'media/partner', 'catering-menu']
    INFO_TAG(f'Firebase initialized.')
    for dir in dir_firebase:
      blob_list = bucket.list_blobs(prefix=f'{dir}')
      for blob in blob_list:
          blob.make_public()
    INFO_TAG(f'Firebase Ready.')
    
        

def get_image(path):
    url = bucket.blob(path)
    return url


# Version 2 (upload with convert to webp extension args)
def firebase_upload(path, img, convert_webp=False):
    now = timezone.now()
    try:
        
        formatted_name = img.name.replace(' ', '-').lower()
        bucket = storage.bucket()
        
        if convert_webp:
            folder_path = f"{path}/{now.strftime('%m-%Y')}-{formatted_name}.webp"
            blob = bucket.blob(folder_path)
            img = convert_compress_image(img)
            blob.upload_from_file(img, content_type='.webp')
        else:
            ct = img.content_type.split('/')[1]  # Mendapatkan tipe konten dari file
            folder_path = f"{path}/{now.strftime('%m-%Y')}-{formatted_name}.{ct}"
            blob = bucket.blob(folder_path)
            blob.upload_from_file(img, content_type=img.content_type)
        
        # Buat URL publik
        blob.make_public()
        public_url = blob.public_url
        
        return (True, public_url)
    except Exception as err:
        print(err)
        return (False, 'Terjadi kesalahan saat upload, silahkan ulangi.')
    
    
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
