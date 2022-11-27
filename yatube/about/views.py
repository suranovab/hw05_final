from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Вывод страницы Об авторе"""

    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Вывод страницы об используемых в проекте технологиях"""

    template_name = 'about/tech.html'
