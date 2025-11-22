"""
Signals to sync Event model with Elasticsearch
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Event
from .documents import EventDocument, get_elasticsearch_connection


@receiver(post_save, sender=Event)
def index_event(sender, instance, **kwargs):
    """
    Index event in Elasticsearch when saved
    """
    # Only index if Elasticsearch is configured
    if not hasattr(settings, 'ELASTICSEARCH_DSL'):
        return
    
    try:
        get_elasticsearch_connection()
        doc = EventDocument.from_event(instance)
        doc.save()
    except Exception as e:
        # Log error but don't fail the save operation
        # In production, consider using logging here
        print(f"Error indexing event {instance.id} in Elasticsearch: {e}")


@receiver(post_delete, sender=Event)
def delete_event_index(sender, instance, **kwargs):
    """
    Delete event from Elasticsearch when deleted
    """
    # Only delete if Elasticsearch is configured
    if not hasattr(settings, 'ELASTICSEARCH_DSL'):
        return
    
    try:
        get_elasticsearch_connection()
        doc = EventDocument()
        doc.meta.id = instance.id
        doc.delete()
    except Exception as e:
        # Log error but don't fail the delete operation
        print(f"Error deleting event {instance.id} from Elasticsearch: {e}")

