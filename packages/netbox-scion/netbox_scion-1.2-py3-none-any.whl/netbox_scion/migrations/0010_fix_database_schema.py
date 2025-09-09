from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_scion', '0009_version_1_2_changes'),
    ]

    operations = [
        # Drop the peer column from Organization table (if it exists)
        migrations.RunSQL(
            "ALTER TABLE netbox_scion_organization DROP COLUMN IF EXISTS peer CASCADE;",
            reverse_sql="-- No reverse operation needed"
        ),
        
        # Add the peer column to SCIONLinkAssignment table (if it doesn't exist)
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'netbox_scion_scionlinkassignment' 
                    AND column_name = 'peer'
                ) THEN
                    ALTER TABLE netbox_scion_scionlinkassignment 
                    ADD COLUMN peer character varying(255) NOT NULL DEFAULT '';
                END IF;
            END $$;
            """,
            reverse_sql="ALTER TABLE netbox_scion_scionlinkassignment DROP COLUMN IF EXISTS peer;"
        ),
        
        # Add the unique constraint for peer per ISD-AS (if it doesn't exist)
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.table_constraints 
                    WHERE constraint_name = 'unique_peer_per_isdas'
                ) THEN
                    ALTER TABLE netbox_scion_scionlinkassignment 
                    ADD CONSTRAINT unique_peer_per_isdas UNIQUE (isd_as_id, peer);
                END IF;
            END $$;
            """,
            reverse_sql="ALTER TABLE netbox_scion_scionlinkassignment DROP CONSTRAINT IF EXISTS unique_peer_per_isdas;"
        ),
    ]
