# Generated by Django 4.2.7 on 2023-12-04 02:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("edc_crf", "0005_alter_crfstatus_options_crfstatus_locale_created_and_more"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="crfstatus",
            name="edc_crf_crf_modifie_6152c9_idx",
        ),
        migrations.AddIndex(
            model_name="crfstatus",
            index=models.Index(
                fields=["modified", "created"], name="edc_crf_crf_modifie_709d43_idx"
            ),
        ),
    ]