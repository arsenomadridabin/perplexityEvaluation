# Generated manually to remove unique_together constraint

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation_app', '0002_dataentry_marked_no_match'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='dataentry',
            unique_together=set(),
        ),
    ] 