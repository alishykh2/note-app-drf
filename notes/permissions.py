from rest_framework import permissions


class IsAuthor(permissions.BasePermission):

    edit_methods = ("PUT", "PATCH", "GET")

    def has_object_permission(self, request, view, obj):
        if obj.author == request.user or request.user in obj.share_with.all():
            return True

        return False
