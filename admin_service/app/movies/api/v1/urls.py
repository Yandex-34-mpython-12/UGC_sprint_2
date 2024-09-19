from movies.api.v1.views import MoviesViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'movies', MoviesViewSet)

urlpatterns = router.urls
