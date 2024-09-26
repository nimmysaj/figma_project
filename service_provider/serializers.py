from rest_framework import serializers
from Accounts.models import ServiceRegister, Collar, Category, Subcategory

class ServiceRegisterSerializer(serializers.ModelSerializer):
    available_lead_balance = serializers.SerializerMethodField()  # Method to calculate available lead balance
    collar_amount = serializers.SerializerMethodField()  # New method to get collar amount


    class Meta:
        model = ServiceRegister
        fields = ['id', 'service_provider', 'title', 'description', 'gstcode', 'category', 'subcategory', 'license', 
                  'image', 'accepted_terms', 'collar', 'available_lead_balance','collar_amount']

    def get_available_lead_balance(self, obj):
        """
        Method to get the available lead balance for a service.
        If the service type is "One Time Lead", the available lead balance is from the collar's lead_quantity.
        Otherwise, for daily work, it's considered infinite.
        """
        if obj.collar:  # Check if collar is not None
            if obj.subcategory.service_type.name == 'One Time Lead':
                # Call update_lead_balance method to update available balance
                return obj.update_lead_balance(0)  # No extra leads to add in this case
        return "Infinite"  # For daily work, there's no limit on the number of leads.
    
    def get_collar_amount(self, obj):
        """Method to return the amount of the selected collar."""
        if obj.collar:
            if obj.subcategory.service_type.name == 'One Time Lead':
                return obj.collar.amount  # Assuming `amount` is a field in the Collar model
        return None  # Return None if no collar is selected
    
    def validate(self, data):
        # Fetch the subcategory instance using the subcategory ID from data
        subcategory = Subcategory.objects.get(id=data['subcategory'].id)
        
        # Check if the service type is "One Time Lead"
        if subcategory.service_type.name == "One Time Lead" and not data.get('collar'):
            raise serializers.ValidationError("Collar is required for One Time Lead services.")
        
        # For daily work, the collar should be treated as 'Infinite'
        if subcategory.service_type.name == "Daily Work":
            data['collar'] = None  # Set collar to None for Daily Work
        
        return data
