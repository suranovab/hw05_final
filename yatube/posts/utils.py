from django.core.paginator import Paginator


def pagination(queryset, request, posts_on_page):
    paginator = Paginator(queryset, posts_on_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
