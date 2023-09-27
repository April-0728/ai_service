from rest_framework import serializers


class LogReduceSerializer(serializers.Serializer):
    algorithm = serializers.ChoiceField(choices=['drain3'], help_text='算法')
    param = serializers.JSONField(required=False, help_text='算法参数')
    model_name = serializers.CharField(max_length=100, required=False, default=None, help_text='模型名称')
    logs = serializers.ListField(child=serializers.CharField(max_length=10000), help_text='日志列表')
