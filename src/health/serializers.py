from rest_framework import serializers


class HealthChecksSerializer(serializers.Serializer):
    app = serializers.CharField()
    db = serializers.CharField()


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    service = serializers.CharField()
    version = serializers.CharField()
    commit = serializers.CharField()
    time = serializers.SerializerMethodField()
    checks = HealthChecksSerializer()

    def get_time(self, obj: dict) -> str:
        value = obj["time"]
        return value.isoformat(timespec="seconds")
