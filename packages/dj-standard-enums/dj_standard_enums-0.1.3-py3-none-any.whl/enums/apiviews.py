from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from enums.framework.registry import SystemEnumRegistry


class RetrieveEnumAPIView(APIView):
    authentication_classes = []  # Add authentication classes if needed
    permission_classes = [AllowAny]  # Add permission classes if needed

    @staticmethod
    def get_enum_representation(enum_class_name, filters=None):
        registry = SystemEnumRegistry()
        enum_class = registry.get_enum_class(class_name=enum_class_name)
        if enum_class is None:
            return []

        full_representation = enum_class.get_full_representation()
        if not filters:
            return full_representation
        filtered_representation = []
        for item in full_representation:
            extra_data, matching = item.get("extra_data", {}), True
            for filter_key, filter_value in filters.items():
                if extra_data.get(filter_key) not in filter_value:
                    matching = False
                    break
            if matching:
                filtered_representation.append(item)
        return filtered_representation

    def get(self, request, *args, **kwargs):
        enum_class_name = kwargs.get("enum_class_name")
        filters = dict(self.request.query_params)
        data = self.get_enum_representation(
            enum_class_name=enum_class_name, filters=filters
        )
        return Response(data=data, status=status.HTTP_200_OK)
