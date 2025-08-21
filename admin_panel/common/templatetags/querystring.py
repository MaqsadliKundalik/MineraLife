from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """
    Joriy URL'dagi GET paramlarni saqlagan holda yangilarini qo'shadi/yangilaydi.
    Foydalanish: ?{% query_transform page=2 %}
    """
    req = context.get("request")
    params = req.GET.copy() if req else {}
    for k, v in kwargs.items():
        if v is None:
            params.pop(k, None)
        else:
            params[k] = v
    return params.urlencode()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
