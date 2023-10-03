from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.models import BaseConstraint
from django.db.models.base import Model

# TODO: Should permit the uniqueness of 
class UniqueActionsConstraint(BaseConstraint):
    def constraint_sql(self, model: type[Model] | None, schema_editor: BaseDatabaseSchemaEditor | None) -> str:
        return super().constraint_sql(model, schema_editor)

    def create_sql(self, model: type[Model] | None, schema_editor: BaseDatabaseSchemaEditor | None) -> str:
        return super().create_sql(model, schema_editor)
    
    def remove_sql(self, model: type[Model] | None, schema_editor: BaseDatabaseSchemaEditor | None) -> str:
        return super().remove_sql(model, schema_editor)
    
    def validate(self, model: type[Model] | None, instance, exclude=None, using="default"):
        pass