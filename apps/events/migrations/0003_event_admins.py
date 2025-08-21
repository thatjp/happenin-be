from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_event_event_type_event_icon_event_is_free_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='admins',
            field=models.ManyToManyField(
                blank=True,
                related_name='admin_events',
                help_text='Users who are admins for this event',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]


