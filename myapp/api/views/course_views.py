from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from myapp.api.models.users import CustomUser, Member
from myapp.api.permissions import HasMemberPermissions
from django.core.cache import cache
from rest_framework import serializers
from django.db.models.signals import post_save
from django.dispatch import receiver

class CourseSerializer(serializers.Serializer):
    department = serializers.CharField(max_length=4)
    number = serializers.CharField(max_length=4)

class CourseEnrollmentViewSet(ViewSet):
    """
    ViewSet for managing a course enrollment dictionary that maps
    course_id -> list of user_ids.

    Format: {
        "CSE 101": ["user_1", "user_2", ...],
        "ECE 110": ["user_4", ...],
        ...
    }
    """
    permission_classes = [HasMemberPermissions]
    queryset = Member.objects.all()
    cache_key = 'course-enrollments'

    def list(self, request):
        enrollments = {}
        for member in self.queryset:
            member_id = str(member.user_id)
            if member.current_courses:
                for course in member.current_courses:
                    course_id = f"{course['department']} {course['number']}"
                    if course_id not in enrollments:
                        enrollments[course_id] = []
                    enrollments[course_id].append(member_id)
        
        cache.set(self.cache_key, enrollments)
        return Response(enrollments, status=status.HTTP_200_OK)

        
    # def list(self, request):
    #     """Lists the current course enrollments."""
    #     enrollments = cache.get(self.cache_key, {})
    #     return Response(enrollments)

    @action(detail=False, methods=['POST'], url_path='enroll')
    def enroll(self, request):
        """Enrolls a user in a course."""
        course_id = request.data.get('course_id')
        user_id = str(request.user.user_id)  # Assuming you want to enroll the requesting user

        if not course_id:
            return Response({'error': 'Course ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        enrollments = cache.get(self.cache_key, {})
        if course_id not in enrollments:
            enrollments[course_id] = []

        if user_id not in enrollments[course_id]:
            enrollments[course_id].append(user_id)
            cache.set(self.cache_key, enrollments)
            return Response({'message': f'User {request.user.preferred_name} enrolled in {course_id}.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': f'User {request.user.preferred_name} is already enrolled in {course_id}.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def drop(self, request):
        """Drops a user from a course."""
        course_id = request.data.get('course_id')
        user_id = str(request.user.user_id)  

        if not course_id:
            return Response({'error': 'Course ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        enrollments = cache.get(self.cache_key, {})
        if course_id in enrollments and user_id in enrollments[course_id]:
            enrollments[course_id].remove(user_id)
            cache.set(self.cache_key, enrollments)
            return Response({'message': f'User {request.user.preferred_name} dropped from {course_id}.'}, status=status.HTTP_200_OK)
        elif course_id not in enrollments:
            return Response({'message': f'Course {course_id} has no enrollments.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': f'User {request.user.preferred_name} is not enrolled in {course_id}.'}, status=status.HTTP_200_OK)
    