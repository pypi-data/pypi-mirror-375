from django.forms.renderers import TemplatesSetting


class TerminusgpsFormRenderer(TemplatesSetting):
    field_template_name = "terminusgps/field.html"
