import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction

from .choices import ChatTypeChoices
from .utils import get_unix_timestamp


class Chat(models.Model):
    """
    Модель чата.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    users = models.ManyToManyField("users.User")
    type = models.CharField(max_length=8, choices=ChatTypeChoices.choices, default=ChatTypeChoices.DEFAULT)
    last_action_time = models.BigIntegerField(default=get_unix_timestamp)


class Message(models.Model):
    """
    Модель сообщения.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    serial_number = models.PositiveIntegerField()
    dialog_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    dialog_id = models.UUIDField()
    dialog = GenericForeignKey("dialog_type", "dialog_id")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    time_create = models.BigIntegerField()

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        if is_new:
            with transaction.atomic():
                last_message = (
                    Message.objects
                    .filter(dialog_type=self.dialog_type, dialog_id=self.dialog_id)
                    .select_for_update()
                    .order_by("-serial_number")
                    .first()
                )
                self.serial_number = (last_message.serial_number + 1) if last_message else 1

        super().save(*args, **kwargs)

        if is_new and isinstance(self.dialog, Chat):
            Chat.objects.filter(id=self.dialog_id).update(last_action_time=self.time_create)
