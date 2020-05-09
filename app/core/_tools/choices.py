from django.utils.translation import ugettext_lazy as _


USERTYPES_CHOICES = (
    (1, _("Admin")),
    (2, _("User"),)
)

FILETYPES_CHOICES = (
    ('', _("Select a permission")),
    ('view', _("Show file")),
    ('view-write', _("Show file and write comment"),)
)
ORDERTYPE_CHOICE = (
    ('', _("Asc")),
    ('-', _("Desc"),)
)
SHAREDFILEMODEL_CHOICES = (
    ('title', _("Title")),
    ('description', _("Description"),),
    ('expiration_date', _("Expiration date"),),
    ('created_date', _("Created date"),),
)