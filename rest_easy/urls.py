from django.conf.urls import url, include
from django.contrib.auth.models import User
from example.models import Person
from rest_framework import routers, serializers, viewsets

import permission
permission.autodiscover()

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')
        
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

# Dynamic Endpoint Generation
from django.conf            import settings
from django.db.models       import get_models, get_app

def generateModelResources():
    
    model_resources = {}
    
    # Loop the registered apps from settings
    for app_name in settings.REST_EASY_APPS:
        
        # Get the models, then loop
        app_models = get_app(app_name)
        for app_model in get_models(app_models):
            
            # Assemble field lists
            model_fields = ()
            for field in app_model._meta.fields:
                if field.name != 'id':
                    model_fields + (field.name,)
            model_properties = {}
            for attribute in dir(app_model):
                if attribute[0:1] != '_' and attribute != 'pk':# and str(app_model.__name__[0:10]) != 'Historical': 
                    try:
                        attribute_value = getattr(app_model,attribute)
                        if isinstance(attribute_value,property):
                            model_properties[attribute] = attribute
                    except:
                        pass

            serializer_dictionary = {}
            
            # Creat the class properties, append to dictionary also append to field names
            for property_name in model_properties:
                serializer_dictionary[property_name] = serializers.Field(source=property_name)
                #model_fields + (property_name,)
                
            # Create Django Rest Framework Serializer
            class_name = app_model.__name__+'Serializer'
            class Meta:
                 model = app_model
                 fields = model_fields
                 
            # Add meta class to dictionary
            serializer_dictionary['Meta'] = Meta
            serializer = type(class_name,(serializers.HyperlinkedModelSerializer,), serializer_dictionary) 
            
            # Create DRF Viewset
            class_name = app_model.__name__.lower()
            if type(app_model._meta.verbose_name_plural) is str: # Inherit Plural (If set)
                class_name = app_model._meta.verbose_name_plural

            queryset = app_model.objects.all()
            # Create class and add to dictionary
            # Don't add Historical Data to API !!! NOTE : This needs to be refactored and data moved into REST_EASY_IGNORE_APPS in settings, to allow for regex matching of terms.
            # Also could add in global permissions rules as REST_EASY_APPS_PERMISSIONS = ( ('Historical*','R')
            if str(app_model.__name__[0:10]) != 'XXXHistorical': 
                model_resources[class_name] = type(class_name,(viewsets.ModelViewSet,), {
                    'queryset' : queryset,
                    'serializer_class' : serializer
                }) 
            
    return model_resources
# Import Model Resource Generator & Register w/ django-rest-framework
model_resources = generateModelResources()
for class_name, class_object in model_resources.iteritems():
    router.register(r''+class_name, class_object)


# End Dynamic Endpoint Generation
# *******************************




# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
               
    # Endpoints
    url(r'^api/', include(router.urls)),
    
    # Auth
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework'))
    
]