from services.firebase import firebase_upload, firebase_delete
from services.logger import logger

def upload_media(path, file, model_instance, field_name, convert_webp=False):
    """
    Uploads media to Firebase and updates model field.
    Returns (success, message)
    """
    try:
        sts, msg = firebase_upload(path=path, img=file, convert_webp=convert_webp)
        if sts:
            setattr(model_instance, field_name, msg)
            model_instance.save()
            logger.info(f'Media uploaded to {path}: {msg}')
            return True, msg
        else:
            logger.error(f'Failed to upload media to {path}')
            return False, msg
    except Exception as e:
        logger.error(f'Error uploading media: {e}')
        return False, str(e)

def delete_media(url):
    """
    Deletes media from Firebase.
    Returns success boolean.
    """
    try:
        success = firebase_delete(url)
        if success:
            logger.info(f'Media deleted: {url}')
        else:
            logger.error(f'Failed to delete media: {url}')
        return success
    except Exception as e:
        logger.error(f'Error deleting media {url}: {e}')
        return False