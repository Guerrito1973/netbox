from django.urls import path

from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("scan/", views.TriggerScanView.as_view(), name="scan"),
    path("map/", views.NetworkMapView.as_view(), name="map"),
    path("hosts/<int:pk>/", views.HostView.as_view(), name="discoveredhost"),
    path("runs/<int:pk>/", views.ScanRunView.as_view(), name="scanrun"),
]

