import os
import time

from app import create_app
from app.services.notification_service import NotificationService

app = create_app()
interval = int(os.getenv("REMINDER_INTERVAL_SECONDS", "60"))

if __name__ == "__main__":
    with app.app_context():
      service = NotificationService()
      print(f"Scheduler uruchomiony. Interwał: {interval}s")

      while True:
          processed = service.send_due_notifications()
          if processed:
              print(f"Przetworzono {len(processed)} powiadomień.")
          time.sleep(interval)