
from django.db import migrations, models


def enable_mdatpinfo_plugin(apps, schema_editor):
    MachineDetailPlugin = apps.get_model("server", "MachineDetailPlugin")

    # Check if plugin already exists to avoid duplicates
    try:
        MachineDetailPlugin.objects.get(name='MDATPInfo')
    except MachineDetailPlugin.DoesNotExist:
        # Get the next order value
        try:
            max_order = MachineDetailPlugin.objects.aggregate(
                models.Max('order'))['order__max'] or 0
        except Exception:
            max_order = 0

        plugin = MachineDetailPlugin(name='MDATPInfo', order=max_order + 1)
        plugin.save()


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0094_auto_20190903_1507'),
    ]

    operations = [
        migrations.RunPython(enable_mdatpinfo_plugin),
    ]
