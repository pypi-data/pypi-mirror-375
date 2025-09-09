from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_scion', '0008_remove_gate_appliance_type'),
    ]

    operations = [
        # First, remove the Organization peer field if it exists
        # (This handles the case where a previous migration added it)
        migrations.RunSQL(
            "ALTER TABLE netbox_scion_organization DROP COLUMN IF EXISTS peer;",
            reverse_sql="-- No reverse operation needed"
        ),
        
        # Remove appliance_type field from ISDAS
        migrations.RemoveField(
            model_name='isdas',
            name='appliance_type',
        ),
        
        # Rename cores to appliances in ISDAS
        migrations.RenameField(
            model_name='isdas',
            old_name='cores',
            new_name='appliances',
        ),
        
        # Update field help text for appliances
        migrations.AlterField(
            model_name='isdas',
            name='appliances',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='List of appliances for this ISD-AS'
            ),
        ),
        
        # Change Organization foreign key to CASCADE for auto-delete
        migrations.AlterField(
            model_name='isdas',
            name='organization',
            field=models.ForeignKey(
                help_text='Organization that operates this ISD-AS',
                on_delete=models.CASCADE,
                related_name='isd_ases',
                to='netbox_scion.organization'
            ),
        ),
        
        # Update core field verbose name and help text in SCIONLinkAssignment
        migrations.AlterField(
            model_name='scionlinkassignment',
            name='core',
            field=models.CharField(
                help_text='Appliance for this assignment',
                max_length=255,
                verbose_name='Appliance'
            ),
        ),
        
        # Rename customer_name to peer_name in SCIONLinkAssignment
        migrations.RenameField(
            model_name='scionlinkassignment',
            old_name='customer_name',
            new_name='peer_name',
        ),
        
        # Update field help text for peer_name
        migrations.AlterField(
            model_name='scionlinkassignment',
            name='peer_name',
            field=models.CharField(
                help_text='Peer name',
                max_length=100
            ),
        ),
        
        # Add peer field to SCIONLinkAssignment
        migrations.AddField(
            model_name='scionlinkassignment',
            name='peer',
            field=models.CharField(
                default='',
                help_text='Peer identifier',
                max_length=255
            ),
            preserve_default=False,
        ),
        
        # Add unique constraint for peer per ISD-AS
        migrations.AddConstraint(
            model_name='scionlinkassignment',
            constraint=models.UniqueConstraint(
                fields=['isd_as', 'peer'],
                name='unique_peer_per_isdas'
            ),
        ),
    ]
