# Notification model import - database table ke saath interact karne ke liye
from Models.notifications import Notification


# NotificationController mein saare notification-related functions hain
class NotificationController:

    @staticmethod
    def get_notifications(data, database):
        # Landlord ID se saare notifications fetch karo, naye se purane order mein
        notifications = database.query(Notification).filter(
            Notification.landlord_id == data.landlord_id
        ).order_by(
            Notification.timestamp.desc()  # Timestamp descending (naye pehle)
        ).all()

        # List of dictionaries return karo
        return [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "is_read": n.is_read,
                "timestamp": n.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for n in notifications
        ]
