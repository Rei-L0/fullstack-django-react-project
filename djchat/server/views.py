from rest_framework.exceptions import ValidationError, AuthenticationFailed
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Count

from .schema import server_list_docs
from .serializer import ServerSerializer
from .models import Server


class ServerListViewSet(viewsets.ViewSet):
    """
    A Google-style doc string.

    This viewset provides facilities for manipulating server information. filter the list of servers, or
    Query and return server information based on specific conditions.

    Attributes:
        queryset (QuerySet): A queryset containing all server objects.

    Methods:
        list(request): Filters server information and responds appropriately to the request.

    Raises:
        AuthenticationFailed: When the user is not authenticated by_user or
            Occurs when the by_serverid query parameter is included in the request.
        ValidationError: If by_serverid is given, the server cannot be found by that id, or
            Occurs when by_serverid or by_user is given an invalid value.
    """

    queryset = Server.objects.all()

    @server_list_docs
    def list(self, request):
        """
        Responds by filtering the list of servers.

        Args:
            request (Request): API request object. Contains filtering options and user authentication information.

        Returns:
            Response: API response object containing serialized, filtered server information.

        Raises:
            AuthenticationFailed: Raised when the user is not authenticated.
                Only checked if the request includes the by_user or by_serverid query parameters.
            ValidationError: If by_serverid is given, the server cannot be found by that id, or
                Occurs when an invalid value is given for by_serverid or by_user.

        How it Works:
            This function filters the list of servers based on several parameters given in the request and generates a response.
            Filtering options include Category, Quantity, By User, and Server ID. according to filter options
            Query the server from the database and serialize it to create a response object.

        Available filtering options are:
            - category (str): Filter by server category name.
            - qty (int): Limits the maximum quantity of servers included in the response.
            - by_user (bool): filter servers based on user id.
            - by_serverid (int): filter servers based on a specific server id.
            - with_num_members (bool): Include the number of members per server in the response.

        sequence of the work:
            1. Perform user authentication check and filter option validation.
            2. Query the server in the database according to each option, such as filtering by category or user.
            3. Count and serialize the number of server members according to the filter options.
            4. Limit the number of servers included in the response.
            5. Filter by server ID to find a server with that ID.

        exception handling:
            - if by_user or by_serverid is included in the request when the user is not authenticated
            Raises an AuthenticationFailed exception.
            - If by_serverid is given, raise a ValidationError exception if the server cannot be found by that id.
            - Raise a ValidationError exception if an invalid value is given for by_serverid or by_user.
        """

        # Extract request parameters used for filtering
        category = request.query_params.get("category")
        qty = request.query_params.get("qty")
        by_user = request.query_params.get("by_user") == "true"
        by_serverid = request.query_params.get("by_serverid")
        with_num_members = request.query_params.get("with_num_members") == "true"

        # Verify user authentication and validate filter options
        # if (by_user or by_serverid) and not request.user.is_authenticated:
        # raise AuthenticationFailed("User authentication is required.")

        # Filter servers by category
        if category:
            self.queryset = self.queryset.filter(category__name=category)

        # Filter server by user
        if by_user:
            if by_user and request.user.is_authenticated:
                user_id = request.user.id
                self.queryset = self.queryset.filter(member=user_id)
            else:
                raise AuthenticationFailed()

        # serialize including number of server members
        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count("member"))

        # Filter and validate by server id
        if by_serverid:
            if not request.user.is_authenticated:
                raise AuthenticationFailed()

            try:
                self.queryset = self.queryset.filter(id=by_serverid)
                if not self.queryset.exists():
                    raise ValidationError(
                        detail=f"Could not find server with ID {by_serverid}"
                    )
            except ValueError:
                raise ValidationError(detail="Server value error")

        # Quantity restrictions apply
        if qty:
            self.queryset = self.queryset[: int(qty)]

        # Generate response with serialized data
        serializer = ServerSerializer(
            self.queryset, many=True, context={"num_members": with_num_members}
        )
        return Response(serializer.data)
