"""parkir URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.conf.urls import url
from parkiran import views
from parkiran.views import Dashboard, Kelola, Keluar, Dibayar, Search, struk_render_to_pdf_view, Tiket, AmbilTiket, AmbilTiketView, AmbilTiket2, TiketBayar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', Dashboard, name='dashboard'),
    path('kelola/', Kelola, name='kelola'),
    path('kelola/<int:pk>/keluar', Keluar, name='keluar'),
    path('kelola/<int:pk>/dibayar', Dibayar, name='dibayar'),
    path('kelola/search/', Search, name='search'),
    path('kelola/pdf/<pk>/', struk_render_to_pdf_view, name='strukpdf'),
    path('tiket/', Tiket, name='tiket'),
    path('tiket/<int:pk>/bayar,', TiketBayar, name='tiketbayar'),
    path('ambiltiket/', AmbilTiket, name='ambiltiket'),
    path('ambiltiket/<int:pk>/', AmbilTiketView.as_view(), name='ambiltiket1'),
    path('ambiltiket/<int:pk>/ambil', AmbilTiket2, name='ambiltiket2'),
    url(r'^media/(?P<path>.*)$', serve,{'document_root':       settings.MEDIA_ROOT}), 
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
