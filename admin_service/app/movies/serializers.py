from movies.models import Filmwork
from rest_framework import serializers


class MoviesSerializer(serializers.ModelSerializer):
    actors = serializers.ListField(read_only=True)
    directors = serializers.ListField(read_only=True)
    writers = serializers.ListField(read_only=True)
    genre = serializers.ListField(read_only=True)

    class Meta:
        model = Filmwork
        fields = (
            "id",
            "title",
            "description",
            "creation_date",
            "rating",
            "type",
            "genre",
            "actors",
            "directors",
            "writers",
        )
