# Generated manually for renaming field and related names

from django.db import migrations


class Migration(migrations.Migration):
    
    dependencies = [
        ('inventory_monitor', '0042_rename_abra_to_external_inventory'),
    ]

    operations = [
        # Step 1: Rename the field abra_id to external_id (only if abra_id exists)
        migrations.RenameField(
            model_name='externalinventory',
            old_name='abra_id',
            new_name='external_id',
        ),
    ]
