from category.models import Category


def list_categories(request):
    categories = Category.objects.all()
    return dict(categories=categories)
