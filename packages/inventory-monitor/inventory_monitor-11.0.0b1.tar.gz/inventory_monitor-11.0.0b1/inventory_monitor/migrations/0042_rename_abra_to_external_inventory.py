# Generated manually for renaming ABRA to ExternalInventory

from django.db import migrations


class Migration(migrations.Migration):
    
    dependencies = [
        ('inventory_monitor', '0041_alter_asset_options_and_more'),
    ]

    def _rename_ct_and_perms_forward(apps, schema_editor):
        ContentType = apps.get_model('contenttypes', 'ContentType')
        Permission = apps.get_model('auth', 'Permission')
        app_label = 'inventory_monitor'
        old_model = 'abra'
        new_model = 'externalinventory'

        new_ct, _ = ContentType.objects.get_or_create(app_label=app_label, model=new_model)
        try:
            old_ct = ContentType.objects.get(app_label=app_label, model=old_model)
        except ContentType.DoesNotExist:
            old_ct = None

        if not old_ct:
            return

        # Update built-in perms; tolerate projects without "view" (older Django).
        for template in ('add_%s', 'change_%s', 'delete_%s', 'view_%s'):
            old_code = template % old_model
            new_code = template % new_model
            # If a new permission already exists, delete it so we can update in-place
            # and preserve the original permission id (keeps existing assignments).
            Permission.objects.filter(content_type=new_ct, codename=new_code).delete()
            try:
                p = Permission.objects.get(content_type=old_ct, codename=old_code)
            except Permission.DoesNotExist:
                continue
            p.codename = new_code
            p.content_type = new_ct
            # Optional: refresh display name if it references the old model.
            p.name = (p.name
                      .replace('ABRA', 'External inventory')
                      .replace('Abra', 'External inventory')
                      .replace('abra', 'external inventory'))
            p.save()

        # Remove stale content type to avoid duplicates.
        old_ct.delete()

    def _rename_ct_and_perms_reverse(apps, schema_editor):
        ContentType = apps.get_model('contenttypes', 'ContentType')
        Permission = apps.get_model('auth', 'Permission')
        app_label = 'inventory_monitor'
        old_model = 'externalinventory'
        new_model = 'abra'

        new_ct, _ = ContentType.objects.get_or_create(app_label=app_label, model=new_model)
        try:
            old_ct = ContentType.objects.get(app_label=app_label, model=old_model)
        except ContentType.DoesNotExist:
            old_ct = None

        if not old_ct:
            return

        for template in ('add_%s', 'change_%s', 'delete_%s', 'view_%s'):
            old_code = template % old_model
            new_code = template % new_model
            Permission.objects.filter(content_type=new_ct, codename=new_code).delete()
            try:
                p = Permission.objects.get(content_type=old_ct, codename=old_code)
            except Permission.DoesNotExist:
                continue
            p.codename = new_code
            p.content_type = new_ct
            p.save()
        old_ct.delete()

    operations = [
        # Step 1: Simply rename the model from ABRA to ExternalInventory
        # This will rename the table from inventory_monitor_abra to inventory_monitor_externalinventory
        migrations.RenameModel(
            old_name='ABRA',
            new_name='ExternalInventory',
        ),
        # Step 2: Update ContentType and permission codenames to preserve assignments
        migrations.RunPython(
            _rename_ct_and_perms_forward,
            _rename_ct_and_perms_reverse,
        ),
    ]
