from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='portal:home'), name='logout'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('scholarships/', views.scholarship_catalog, name='scholarship_catalog'),
    path('scholarships/<int:pk>/', views.scholarship_program_detail, name='program_detail'),
    path('scholarships/add/', views.AddScholarshipView.as_view(), name='add_scholarship'),
    path('coordinator/', views.coordinator_dashboard, name='coordinator_dashboard'),
    path('admin/coordinator/', views.CoordinatorListView.as_view(), name='coordinator_list'),
    path('admin/coordinator/add/', views.AddCoordinatorView.as_view(), name='add_coordinator'),
    path('admin/scholarship-types/', views.ScholarshipTypeListView.as_view(), name='scholarship_type_list'),
    path('admin/scholarship-types/add/', views.AddScholarshipTypeView.as_view(), name='add_scholarship_type'),
    path('applications/create/', views.application_create, name='application_create'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('api/token/', views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/verify/<int:pk>/', views.ApplicationStatusAPIView.as_view(), name='api_verify'),
]
