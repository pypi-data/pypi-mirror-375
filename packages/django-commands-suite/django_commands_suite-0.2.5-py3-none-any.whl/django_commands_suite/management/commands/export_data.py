import csv
import os
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.core import serializers

class Command(BaseCommand):

    help = "Export model data to CSV or JSON"

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            type=str,
            required=True,
            help="Model to export (e.g. myapp.MyModel)"
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=["csv", "json"],
            default="json",
            help="Export format: csv or json (default: json)"
        )
        parser.add_argument(
            "--output",
            type=str,
            help="Output file name (optional)"
        )

    def handle(self, *args, **options):
        model_path = options["model"]
        export_format = options["format"]
        output_file = options["output"]

        try:
            app_label, model_name = model_path.split(".")
            model = apps.get_model(app_label, model_name)
        except (ValueError, LookupError):
            raise CommandError("Invalid model. Use format: app_label.ModelName")
        
        queryset = model.objects.all()

        if not queryset.exists():
            self.stdout.write(self.style.WARNING("No data found in model."))
            return

        if not output_file:
            output_file = f"{model_name.lower()}.{export_format}"

        if export_format == "json":
            self.export_json(queryset, output_file)
        elif export_format == "csv":
            self.export_csv(queryset, model, output_file)

        self.stdout.write(
            self.style.SUCCESS(f"Exported {queryset.count()} records to {os.path.abspath(output_file)}")
        )

    def export_json(self, queryset, output_file):
        data = serializers.serialize("json", queryset, indent=4)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(data)
    
    def export_csv(self, queryset, model, output_file):
        field_names = [field.name for field in model._meta.fields]
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(field_names)
            for obj in queryset:
                writer.writerow([getattr(obj, field) for field in field_names])
