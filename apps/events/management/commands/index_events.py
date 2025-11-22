"""
Management command to index all events in Elasticsearch
"""
from django.core.management.base import BaseCommand
from apps.events.models import Event
from apps.events.documents import EventDocument, get_elasticsearch_connection
from django.conf import settings


class Command(BaseCommand):
    help = 'Index all events in Elasticsearch'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-index',
            action='store_true',
            help='Delete existing index before reindexing',
        )
        parser.add_argument(
            '--create-index',
            action='store_true',
            help='Create the index if it does not exist',
        )

    def handle(self, *args, **options):
        if not hasattr(settings, 'ELASTICSEARCH_DSL'):
            self.stdout.write(
                self.style.ERROR('Elasticsearch is not configured in settings')
            )
            return

        try:
            # Initialize connection and test it
            self.stdout.write('Connecting to Elasticsearch...')
            conn = get_elasticsearch_connection()
            
            # Test connection
            try:
                health = conn.cluster.health(request_timeout=5)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Connected to Elasticsearch cluster: {health.get("cluster_name", "unknown")}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Cannot connect to Elasticsearch. Please ensure Elasticsearch is running.\n'
                        f'Error: {e}'
                    )
                )
                return
            
            # Delete index if requested
            if options['delete_index']:
                self.stdout.write('Deleting existing index...')
                try:
                    if EventDocument._index.exists():
                        EventDocument._index.delete()
                        self.stdout.write(self.style.SUCCESS('Index deleted'))
                    else:
                        self.stdout.write(
                            self.style.WARNING('Index does not exist, nothing to delete')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Could not delete index: {e}')
                    )
            
            # Create index if requested or if it doesn't exist
            if options['create_index']:
                self.stdout.write('Creating index...')
                try:
                    if EventDocument._index.exists():
                        self.stdout.write(
                            self.style.WARNING(
                                f'Index "{EventDocument._index._name}" already exists. '
                                'Use --delete-index to recreate it.'
                            )
                        )
                    else:
                        EventDocument._index.create()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Index "{EventDocument._index._name}" created successfully'
                            )
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Could not create index: {e}')
                    )
                    import traceback
                    self.stdout.write(traceback.format_exc())
                    return
            
            # Get all active events
            events = Event.objects.filter(is_active=True)
            total = events.count()
            
            self.stdout.write(f'Indexing {total} events...')
            
            indexed = 0
            failed = 0
            
            for event in events:
                try:
                    doc = EventDocument.from_event(event)
                    doc.save()
                    indexed += 1
                    
                    if indexed % 100 == 0:
                        self.stdout.write(f'Indexed {indexed}/{total} events...')
                
                except Exception as e:
                    failed += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'Failed to index event {event.id}: {e}'
                        )
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully indexed {indexed} events. Failed: {failed}'
                )
            )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error indexing events: {e}')
            )

