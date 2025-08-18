from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.notifications.services import NotificationTemplateService
from apps.notifications.models import NotificationPreference, NotificationType

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up default notification templates and preferences'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-templates',
            action='store_true',
            help='Create default notification templates',
        )
        parser.add_argument(
            '--create-preferences',
            action='store_true',
            help='Create default notification preferences for all users',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Create both templates and preferences',
        )

    def handle(self, *args, **options):
        if options['all'] or options['create_templates']:
            self.create_templates()
        
        if options['all'] or options['create_preferences']:
            self.create_preferences()
        
        if not any([options['create_templates'], options['create_preferences'], options['all']]):
            self.stdout.write(
                self.style.WARNING(
                    'No action specified. Use --create-templates, --create-preferences, or --all'
                )
            )

    def create_templates(self):
        """Create default notification templates"""
        self.stdout.write('Creating default notification templates...')
        
        try:
            templates = NotificationTemplateService.create_default_templates()
            
            if templates:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created {len(templates)} default templates:'
                    )
                )
                for template in templates:
                    self.stdout.write(f'  - {template.name} ({template.notification_type})')
            else:
                self.stdout.write(
                    self.style.WARNING('All default templates already exist')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating templates: {e}')
            )

    def create_preferences(self):
        """Create default notification preferences for all users"""
        self.stdout.write('Creating default notification preferences...')
        
        try:
            users = User.objects.all()
            notification_types = [choice[0] for choice in NotificationType.choices]
            
            created_count = 0
            updated_count = 0
            
            for user in users:
                for notification_type in notification_types:
                    preference, created = NotificationPreference.objects.get_or_create(
                        user=user,
                        notification_type=notification_type,
                        defaults={
                            'in_app_enabled': True,
                            'email_enabled': True,
                            'sms_enabled': False,
                            'push_enabled': True
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        # Update existing preferences to ensure they have all fields
                        if not hasattr(preference, 'sms_enabled'):
                            preference.sms_enabled = False
                            preference.save()
                            updated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {created_count} preferences and updated {updated_count} existing ones'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating preferences: {e}')
            )
