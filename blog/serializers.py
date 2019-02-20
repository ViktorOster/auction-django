from rest_framework import serializers
from blog.models import Post

class postSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        #fiels = ('author', 'title')
        fields = '__all__'
