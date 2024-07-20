from rest_framework import serializers
from interview.models import Interview
from authentication.models import User
from dateutil import parser

class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['user', 'resume', 'parsed_resume', 'interview_code', 'job_title', 'job_description', 'company_name', 'interview_type', 'interview_status', 'interview_date', 'feedback', 'feedback_rating', 'stage']

    def create(self, validated_data):
        resume = validated_data.pop('resume') # assuming resume is a list
        interview = Interview.objects.create(resume=resume, **validated_data)
        interview.parsed_resume = interview.parse_resume(resume)
        interview.save()
        return interview

    def update(self, instance, validated_data):
        if 'resume' in validated_data:
            instance.resume.delete()
            instance.resume = validated_data.pop('resume')[0]
            instance.parsed_resume = instance.parse_resume(instance.resume)
            instance.save()
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = instance.user.email
        return response

    def to_internal_value(self, data):
        data = data.copy()
        user = data.get('user')
        if user:
            user = User.objects.get(email=user)
            data['user'] = user.email
        return super().to_internal_value(data)
