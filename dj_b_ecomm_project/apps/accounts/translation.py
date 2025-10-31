from modeltranslation.translator import register, TranslationOptions
from .models import CustomUser

@register(CustomUser)
class UserTranslationOptions(TranslationOptions):
    fields = ('bio', 'location', 'display_name')