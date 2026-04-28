from app.services.notification_service import NotificationService


def send_due_reminders_command():
    service = NotificationService()
    sent_items = service.send_due_notifications()
    print(f"Przetworzono {len(sent_items)} powiadomień.")
