from rest_framework import serializers
from conversation.models import Video, Conversation
from authentication.api.serializers import UserSerializer
import json

class TranscriptField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, list):
            raise serializers.ValidationError('Transcript must be a list of objects.')
        
        for item in data:
            if not isinstance(item, dict):
                raise serializers.ValidationError('Each item in the transcript must be an object.')
            if 'text' not in item or 'start' not in item or 'duration' not in item:
                raise serializers.ValidationError('Each item must contain text, start, and duration fields.')
            if not isinstance(item['text'], str) or not isinstance(item['start'], (int, float)) or not isinstance(item['duration'], (int, float)):
                raise serializers.ValidationError('Invalid types for text, start, or duration fields.')
        
        return json.dumps(data)

    def to_representation(self, value):
        return json.loads(value)


class DescriptionField(serializers.Field):
    def to_internal_value(self, data):
        # Validate that the input is a dictionary with the expected keys and types
        if not isinstance(data, dict):
            raise serializers.ValidationError('Description must be a dictionary.')
        
        required_keys = {
            'publishedAt': str,
            'channelId': str,
            'title': str,
            'description': str,
            'thumbnails': dict,
            'channelTitle': str,
            'tags': list,
            'categoryId': str,
            'liveBroadcastContent': str,
            'localized': dict,
            'defaultAudioLanguage': str,
        }

        for key, value_type in required_keys.items():
            if key not in data:
                raise serializers.ValidationError(f'Missing key: {key}')
            if not isinstance(data[key], value_type):
                raise serializers.ValidationError(f'Invalid type for key: {key}')

        # Validate nested dictionaries if necessary
        thumbnail_keys = {'default', 'medium', 'high', 'standard', 'maxres'}
        for key in thumbnail_keys:
            if key in data['thumbnails']:
                if not isinstance(data['thumbnails'][key], dict):
                    raise serializers.ValidationError(f'Thumbnail key {key} must be a dictionary.')

        if 'localized' in data:
            localized_keys = {'title', 'description'}
            for key in localized_keys:
                if key in data['localized']:
                    if not isinstance(data['localized'][key], str):
                        raise serializers.ValidationError(f'Localized key {key} must be a string.')

        return json.dumps(data)  # Convert the validated data to JSON string for storage

    def to_representation(self, value):
        # Convert the JSON string back to a Python object
        return json.loads(value)


class VideoSerializer(serializers.ModelSerializer):
    transcript = TranscriptField()
    description = DescriptionField()
    class Meta:
        model = Video
        fields = ['videoId', 'transcript', 'description', 'visual_data']

class ConversationSerializer(serializers.ModelSerializer):
    videoId = VideoSerializer()
    username = UserSerializer()
    
    class Meta:
        model = Conversation
        fields = ['id', 'videoId', 'username', 'timestamp', 'timestamp', 'text', 'response']
