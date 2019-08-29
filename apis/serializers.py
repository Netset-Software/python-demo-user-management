
from rest_framework import serializers
from apis.models import *

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'phone', 'country', 'city', 'address', 'zip', 'image', 'sign_up_status', 'social_id', 'created_time', 'role')
        
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'price', 'description', 'is_active', 'created_time', 'added_by')
    
    
    