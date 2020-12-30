from django.urls import path
from crawler import views

urlpatterns = [
    path('',views.index, name = 'index'),
    path('crawlAll',views.crawlAll, name = 'crawlAll'),
    path('<int:stid>',views.crawlSingle, name = 'crawlSingle'),
]