# Generated by Django 4.2.7 on 2023-12-04 22:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("edc_crf", "0006_remove_crfstatus_edc_crf_crf_modifie_6152c9_idx_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="crfstatus",
            index=models.Index(
                fields=["subject_identifier"], name="edc_crf_crf_subject_e09e96_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="crfstatus",
            index=models.Index(
                fields=[
                    "schedule_name",
                    "visit_schedule_name",
                    "visit_code",
                    "visit_code_sequence",
                ],
                name="edc_crf_crf_schedul_f8d84b_idx",
            ),
        ),
    ]
