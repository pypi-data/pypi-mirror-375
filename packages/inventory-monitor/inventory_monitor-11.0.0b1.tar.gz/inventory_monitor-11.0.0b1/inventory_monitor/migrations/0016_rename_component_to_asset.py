from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("inventory_monitor", "0015_alter_component_table"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Component",
            new_name="Asset",
        ),
    ]
