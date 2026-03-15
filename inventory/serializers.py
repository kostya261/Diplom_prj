from rest_framework import serializers
from .models import StorageLocation, ToolCategory, ToolManufacturer, Tool, ToolIssue


class StorageLocationSerializer(serializers.ModelSerializer):
    full_path = serializers.CharField(source='get_full_path', read_only=True)

    class Meta:
        model = StorageLocation
        fields = '__all__'


class ToolCategorySerializer(serializers.ModelSerializer):
    full_path = serializers.CharField(source='get_full_path', read_only=True)

    class Meta:
        model = ToolCategory
        fields = '__all__'


class ToolManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolManufacturer
        fields = '__all__'


class ToolSerializer(serializers.ModelSerializer):
    category_full_path = serializers.CharField(source='category.get_full_path', read_only=True)
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)
    location_full_path = serializers.CharField(source='location.get_full_path', read_only=True)

    class Meta:
        model = Tool
        fields = '__all__'


class ToolIssueSerializer(serializers.ModelSerializer):
    tool_name = serializers.CharField(source='tool.name', read_only=True)
    issued_to_name = serializers.CharField(source='issued_to.get_full_name', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.get_full_name', read_only=True)
    returned_to_name = serializers.CharField(source='returned_to.get_full_name', read_only=True)

    class Meta:
        model = ToolIssue
        fields = '__all__'
        read_only_fields = ['issued_at']
