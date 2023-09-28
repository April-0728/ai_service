from rest_framework import serializers


class DataInsightLogReduceRequest(serializers.Serializer):
    begin = serializers.DateTimeField(help_text='开始时间')
    end = serializers.DateTimeField(help_text='结束时间')
    query = serializers.CharField(max_length=10000, help_text='查询语句')

    algorithm = serializers.ChoiceField(choices=['drain3'], help_text='算法')
    model_name = serializers.CharField(max_length=100, required=False, default='', allow_blank=True,
                                       help_text='模型名称')
    param = serializers.JSONField(required=False, help_text='算法参数', default={})
