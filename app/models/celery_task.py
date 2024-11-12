from celery.result import AsyncResult

class CeleryTask:
    @staticmethod
    def get_status(task_id):
        task_result = AsyncResult(task_id)
        return {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None
        }
