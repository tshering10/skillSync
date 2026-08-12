from rest_framework.routers import DefaultRouter
from .views import MatchViewSet

router = DefaultRouter()
router.register(r'', MatchViewSet, basename='match')

urlpatterns = router.urls
