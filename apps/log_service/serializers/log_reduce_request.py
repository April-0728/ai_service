from rest_framework import serializers


class LogReduceRequest(serializers.Serializer):
    algorithm = serializers.ChoiceField(choices=['drain3'], help_text='算法')
    param = serializers.JSONField(required=False, allow_null=True, default={}, help_text='算法参数')
    model_name = serializers.CharField(max_length=100, allow_blank=True, allow_null=True, required=False, default="",
                                       help_text='模型名称')
    logs = serializers.ListField(child=serializers.CharField(max_length=10000), help_text='日志列表')
