# need add to head urls.py
#from django.conf.urls import handler404, handler500
#handler404 = 'posts.views.page_not_found'
#handler500 = 'posts.views.server_error'



def page_not_found(request, exception):
    return render(
        request, "misc/404.html", {"path": request.path},
        status=HTTPStatus.NOT_FOUND
    )


def server_error(request):
    return render(
        request, "misc/500.html",
        status=HTTPStatus.INTERNAL_SERVER_ERROR)


def pagination(request, objects):
    """Рутина подготовки Пагинатора для страниц.

    аргументы:
    request - HttpRequest от запрошенной страницы, содержит номер страницы,
              для которой нужно вывести порцию объектов
    objects - набор объектов, которые надо разбить постранично
    return - порция объектов для номера страницы из request
    """
    paginator = Paginator(objects, settings.PAGINATOR_DEFAULT_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page