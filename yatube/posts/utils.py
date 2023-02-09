from django.core.paginator import Paginator

NUMBER_OF_POSTS_ON_PAGE = 10


def paginator_func(request, posts):
    paginator = Paginator(posts, NUMBER_OF_POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
