import logging
import uuid

from django.db import models

log = logging.getLogger(__name__)


class CommonBaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # history = HistoricalRecords(
    #     inherit=True,
    #     bases=[RequestIDHistoricalModel, ]
    # )

    class Meta:
        abstract = True
        ordering = ['-updated']

    # @property
    # def audit_entry(self):
    #     latest = self.history.latest()
    #     return {
    #         'id': str(latest.history_id),
    #         'reason': latest.history_change_reason
    #     }
