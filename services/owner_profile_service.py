from apps.models import OwnerProfile
from services.logger import logger

def update_owner_profile(post_data):
    """
    Updates OwnerProfile records from POST data.
    Converts keys with '-' to '_' and creates/updates records.
    """
    try:
        for key, value in post_data.items():
            key_correction = str(key).replace('-', '_')
            try:
                exist_data = OwnerProfile.objects.get(info=key_correction)
                exist_data.content = value
                exist_data.save()
            except OwnerProfile.DoesNotExist:
                new_data = OwnerProfile(info=key_correction, content=value)
                new_data.save()

        logger.info('OwnerProfile data updated successfully.')
        return True
    except Exception as err_update_owner:
        logger.error('Error when updating OwnerProfile')
        logger.error(err_update_owner)
        return False
        