from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from django.core.exceptions import ValidationError
from .models import DemographicData

class DemographicDataResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        # Validate population numbers
        try:
            population = int(row.get('total_village_population', 0))
            converts = int(row.get('converts', 0))
            if population < 0 or converts < 0:
                raise ValidationError("Population and converts must be positive numbers")
            if converts > population:
                raise ValidationError("Number of converts cannot exceed total population")
        except ValueError:
            raise ValidationError("Population and converts must be valid numbers")

    class Meta:
        model = DemographicData
        import_id_fields = ('id',)
        fields = ('id', 'state', 'village', 'total_village_population', 'converts')
        export_order = fields