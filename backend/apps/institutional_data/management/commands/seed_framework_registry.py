from django.core.management.base import BaseCommand
from apps.institutional_data.models import Framework


FRAMEWORKS = [
    ("naac", "NAAC", "National Assessment and Accreditation Council", "Institutional accreditation and quality assurance."),
    ("nba", "NBA", "National Board of Accreditation", "Programme-level accreditation, including outcomes-based education."),
    ("nirf", "NIRF", "National Institutional Ranking Framework", "Institutional ranking data and metrics."),
    ("aicte", "AICTE", "All India Council for Technical Education", "Applicable approvals and mandatory disclosures."),
    ("iic", "IIC", "Institution's Innovation Council / Ministry of Education", "Innovation, entrepreneurship, activities and outcomes."),
    ("aishe", "AISHE", "All India Survey on Higher Education", "Annual higher-education statistical return."),
    ("affiliation", "Affiliation / University", "Affiliating university and applicable state authorities", "Affiliation, intake, inspection and renewal requirements."),
    ("ugc", "UGC", "University Grants Commission", "Applicable recognition, regulations and disclosures."),
]


class Command(BaseCommand):
    help = "Create or update the base framework registry. Does not load or certify official metric definitions."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        for code, name, authority, description in FRAMEWORKS:
            obj, created = Framework.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "authority": authority,
                    "description": description,
                    "is_enabled": True,
                    "is_system": True,
                },
            )
            created_count += int(created)
            updated_count += int(not created)
        self.stdout.write(self.style.SUCCESS(
            f"Framework registry complete: {created_count} created, {updated_count} updated. "
            "Editions, criteria, metrics and formulae must be loaded from reviewed, versioned configuration."
        ))
