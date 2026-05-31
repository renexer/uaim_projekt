from backend.app.celery_app import Celery

def make_celery(app_name, broker_url, backend_url):
    celery = Celery(app_name, broker=broker_url, backend=backend_url)
    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
    return celery