from netbox.api.routers import NetBoxRouter

from .views import DiscoveredHostViewSet, ScanRunViewSet

router = NetBoxRouter()
router.register("hosts", DiscoveredHostViewSet)
router.register("runs", ScanRunViewSet)
urlpatterns = router.urls

