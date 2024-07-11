# urls.py

from django.urls import path
from . import views
from .views import kanzyatouroku_view, itiranhyouzi_view
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.login_view, name='login'),  # ログイン画面のURL
    path('tourokukinou/', views.tourokukinou_view, name='tourokukinou'),
    path('kanrisya_login/', views.kanrisya_login_view, name='kanrisya_login'),
    path('logout/', views.logout_view, name='logout'),
    path('tuika/', views.tuika_view, name='tuika'),
    path('confirm_tabyouin/', views.confirm_tabyouin, name='confirm_tabyouin'),
    path('confirm_tabyouin_submission/', views.confirm_tabyouin_submission, name='confirm_tabyouin_submission'),
    path('itiranhyouzi/', itiranhyouzi_view, name='itiranhyouzi'),
    path('zyuusyokensaku/', views.zyuusyokensaku, name='zyuusyokensaku'),
    path('simeihenkou/', views.simeihenkou_view, name='simeihenkou'),
    path('update_employee_name', views.update_employee_name, name='update_employee_name'),
    path('zyouhouhenkou/', views.zyouhouhenkou_view, name='zyouhouhenkou'),

    path('uketuke_login/', views.uketuke_login, name='uketuke_login'),
    path('kanzyatouroku/', kanzyatouroku_view, name='kanzyatouroku'),
    path('success/', TemplateView.as_view(template_name='success.html'), name='success'),
    path('kanzyakanri/', views.kanzyakanri_view, name='kanzyakanri'),
    path('hokensyokensaku/', views.hokensyokensaku_view, name='hokensyokensaku'),

    path('isya_login/', views.isya_login_view, name='isya_login'),
    path('success_k/', TemplateView.as_view(template_name='success_k.html'), name='success_k'),
    path('kanzyakensaku/', views.kanzyakensaku_view, name='kanzyakensaku'),
    path('confirmation_page/', views.medication_confirmation_view, name='medication_confirmation'),
    path('kusuri_tuika/', views.kusuri_tuika, name='kusuri_tuika'),
    path('kusuri_tuikakakunin/', views.kusuri_tuikakakunin_view, name='kusuri_tuikakakunin'),
    path('kusuri_sakuzyo/', views.kusuri_sakuzyo_view, name='kusuri_sakuzyo'),
    path('syoti_kakutei/', views.syoti_kakutei_view, name='syoti_kakutei'),
]


