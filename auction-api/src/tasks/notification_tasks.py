from src.tasks.celery_app import celery_app


@celery_app.task(name="send_outbid_notification")
def send_outbid_notification(user_id: int, auction_id: int, new_amount: str):
    """Notify a user they've been outbid."""
    # TODO: implement email + in-app notification
    pass


@celery_app.task(name="send_auction_won_notification")
def send_auction_won_notification(user_id: int, auction_id: int, amount: str):
    """Notify the winner of an auction."""
    # TODO: implement email + in-app notification
    pass
