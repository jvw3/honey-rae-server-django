"""View module for handling requests for customer data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket, Employee, Customer


class TicketView(ViewSet):
    """Honey Rae API tickets view"""

    def create(self, request):
        """Handle POST requests for service tickets

        Returns:
            Response: JSON serialized representation of newly created service ticket
        """
        # create a new instance of the service ticket database model class
        new_ticket = ServiceTicket()
        # Customer.objects.get(user=request.auth.user) is a massive black box where we just need to know what Django does.
        # When we sent the post request, we sent the authorization token. Django goes ahead and find the related user from the database that matches that token.
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        # we get the description from the request.data aka post body. The information that is sent be the client is wrapped up by django in request.data.
        new_ticket.description = request.data['description']
        new_ticket.emergency = request.data['emergency']
        new_ticket.save()

        serialized = TicketSerializer(new_ticket, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)
    def list(self, request):
        """Handle GET requests to get all tickets

        Returns:
            Response -- JSON serialized list of tickets
        """

        service_tickets = []


        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()

            if "status" in request.query_params:
                if request.query_params['status'] == "done":
                    service_tickets = service_tickets.filter(date_completed__isnull=False)

                if request.query_params['status'] == "all":
                    pass

        else:
            service_tickets = ServiceTicket.objects.filter(customer__user=request.auth.user)

        serialized = TicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single customer

        Returns:
            Response -- JSON serialized customer record
        """

        customer = ServiceTicket.objects.get(pk=pk)
        serialized = TicketSerializer(customer, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):

        # select the targeted ticket using pk
        ticket = ServiceTicket.objects.get(pk=pk)

        # get the employee id from the client request
        employee_id = request.data['employee']

        # Select the employee from the database using that id
        assigned_employee = Employee.objects.get(pk=employee_id)

        # assign that employee instance to the employee property of the ticket.
        ticket.employee = assigned_employee

        # now we'll save the updated ticket.
        ticket.save()

        # We're not sending back body but we're sending back the operation was successful with a 204.
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    
    def destroy(self, request, pk=None):
        """Handle delete requests for service tickets"""
        
        service_ticket = ServiceTicket.objects.get(pk=pk)
        service_ticket.delete()
        
        return Response(None, status=status.HTTP_204_NO_CONTENT)



class TicketEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'specialty', 'full_name')

class TicketCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'full_name', 'address')


class TicketSerializer(serializers.ModelSerializer):
    """JSON serializer for tickets"""

    employee = TicketEmployeeSerializer(many=False)
    customer = TicketCustomerSerializer(many=False)
    class Meta:
        model = ServiceTicket
        fields = ('id', 'customer', 'employee', 'description', 'emergency', 'date_completed' )
        depth = 1