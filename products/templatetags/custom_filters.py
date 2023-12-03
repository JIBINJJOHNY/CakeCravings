from django import template

register = template.Library()

@register.filter(name='get_category_count')
def get_category_count(product_counts, category_name):
    for count in product_counts:
        if count['category__name'] == category_name:
            return count['count']
    return 0
