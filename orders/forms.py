from django import forms
from .models import Order, MedicineReminder, Subscription

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip_code', 'shipping_phone', 'payment_method']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'shipping_city': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_state': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Cash on Delivery', 'Cash on Delivery'),
                ('Credit Card', 'Credit Card'),
                ('Debit Card', 'Debit Card'),
                ('Bank Transfer', 'Bank Transfer'),
            ]),
        }

class MedicineReminderForm(forms.ModelForm):
    class Meta:
        model = MedicineReminder
        fields = ['reminder_name', 'product', 'dosage', 'frequency', 'custom_days', 'reminder_time', 'notification_type', 'start_date', 'end_date']
        widgets = {
            'reminder_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Morning Medicine'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1 tablet'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'custom_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Monday, Wednesday, Friday'}),
            'reminder_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notification_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class SubscriptionForm(forms.ModelForm):
    # Custom date fields for better user experience
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False,
        help_text="When should the subscription start? (Leave empty for immediate start)"
    )
    expiry_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False,
        help_text="When should the subscription expire? (Leave empty for 1 year from start)"
    )
    
    class Meta:
        model = Subscription
        fields = ['product', 'quantity', 'frequency', 'auto_billing', 'payment_method', 'shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip_code', 'shipping_phone']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'auto_billing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Cash on Delivery', 'Cash on Delivery'),
                ('Credit Card', 'Credit Card'),
                ('Debit Card', 'Debit Card'),
                ('Bank Transfer', 'Bank Transfer'),
            ]),
            'shipping_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'shipping_city': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_state': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pop 'user' from kwargs before calling super
        super().__init__(*args, **kwargs)
        # Set initial values for shipping info if user has previous orders
        if user:
            last_order = Order.objects.filter(user=user).order_by('-created_at').first()
            if last_order:
                self.fields['shipping_address'].initial = last_order.shipping_address
                self.fields['shipping_city'].initial = last_order.shipping_city
                self.fields['shipping_state'].initial = last_order.shipping_state
                self.fields['shipping_zip_code'].initial = last_order.shipping_zip_code
                self.fields['shipping_phone'].initial = last_order.shipping_phone
    
    def save(self, commit=True):
        subscription = super().save(commit=False)
        
        # Handle start_date
        if self.cleaned_data.get('start_date'):
            from datetime import datetime
            start_date = self.cleaned_data['start_date']
            subscription.start_date = datetime.combine(start_date, datetime.min.time())
        else:
            subscription.start_date = None  # Will be set in model's save method
        
        # Handle expiry_date
        if self.cleaned_data.get('expiry_date'):
            from datetime import datetime
            expiry_date = self.cleaned_data['expiry_date']
            subscription.expiry_date = datetime.combine(expiry_date, datetime.min.time())
        else:
            subscription.expiry_date = None  # Will be set in model's save method
        
        if commit:
            subscription.save()
        return subscription 