from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from movies.models import Filmwork, RoleType
from movies.paginators import StandardResultsSetPagination
from movies.serializers import MoviesSerializer
from rest_framework.viewsets import GenericViewSet, mixins


class MoviesViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = MoviesSerializer
    queryset = Filmwork.objects.prefetch_related("persons", "genres").annotate(
        actors=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=RoleType.ACTOR)),
        directors=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=RoleType.DIRECTOR)),
        writers=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=RoleType.WRITER)),
        genre=ArrayAgg("genres__name", distinct=True)
    )
    pagination_class = StandardResultsSetPagination
