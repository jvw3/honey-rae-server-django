"""View module for handling requests for customer data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import Employee


class EmployeeView(ViewSet):
    """Honey Rae API employees view"""
    def list(self, request):
        """Handle GET requests to get all employees

        Returns:
            Response -- JSON serialized list of employees
        """

        employees = Employee.objects.all()
        serialized = CustomerSerializer(employees, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single customer

        Returns:
            Response -- JSON serialized customer record
        """

        customer = Employee.objects.get(pk=pk)
        serialized = CustomerSerializer(customer, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)


class CustomerSerializer(serializers.ModelSerializer):
    """JSON serializer for employees"""
    class Meta:
        model = Employee
        fields = ('id', 'user', 'specialty', 'full_name',)
        depth = 1