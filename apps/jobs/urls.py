from rest_framework.routers import DefaultRouter
from .views import JobDescriptionViewSet

router = DefaultRouter()
router.register(r'', JobDescriptionViewSet, basename='job')

urlpatterns = router.urls
