# import logging
# logger = logging.getLogger(__name__)

def custom_user_details(strategy, details, user=None, *args, **kwargs):
    # logger.info(f"User details received: {details}")
    if user:
        user.full_name = details.get('fullname', user.full_name)
        user.email = details.get('email', user.email)
        user.save()
