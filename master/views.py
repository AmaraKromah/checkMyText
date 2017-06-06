from django.shortcuts import render
from django.views.generic import View


class IndexView(View):
    template_name = 'account/index.html'

    # def get_queryset(self):
    #     return " "

    @staticmethod
    def get(request):
        return render(request, 'master/base.html')
