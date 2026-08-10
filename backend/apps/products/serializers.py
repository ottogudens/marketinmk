from rest_framework import serializers
from .models import Category, Product, Offer, OfferRedemption, OfferView

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'order']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'name', 'description',
            'price', 'image', 'short_description', 'active'
        ]


class OfferSerializer(serializers.ModelSerializer):
    """Serializer para Ofertas (versión pública)"""
    products = ProductSerializer(many=True, read_only=True)
    days_remaining = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Offer
        fields = [
            'id', 'name', 'description', 'offer_type', 'discount_value',
            'discount_type', 'banner_image', 'cta_text', 'start_date',
            'end_date', 'is_active', 'days_remaining', 'products',
            'min_purchase'
        ]


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de Ofertas (admin)"""
    products = ProductSerializer(many=True, read_only=True)
    redemptions_count = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Offer
        fields = [
            'id', 'name', 'description', 'offer_type', 'discount_value',
            'discount_type', 'banner_image', 'cta_text', 'start_date',
            'end_date', 'status', 'products', 'min_purchase', 'max_uses',
            'uses_count', 'target_all', 'target_first_time', 'target_repeat',
            'min_visits', 'show_on_splash', 'send_whatsapp',
            'whatsapp_delay_minutes', 'created_at', 'updated_at',
            'is_active', 'days_remaining', 'redemptions_count', 'views_count'
        ]
    
    def get_redemptions_count(self, obj):
        return obj.redemptions.count()
    
    def get_views_count(self, obj):
        return obj.views.count()


class OfferRedemptionSerializer(serializers.ModelSerializer):
    offer_name = serializers.CharField(source='offer.name', read_only=True)
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    
    class Meta:
        model = OfferRedemption
        fields = [
            'id', 'offer', 'offer_name', 'client', 'client_name',
            'redeemed_at', 'value_applied', 'amount_spent', 'transaction_id'
        ]


class OfferViewSerializer(serializers.ModelSerializer):
    offer_name = serializers.CharField(source='offer.name', read_only=True)
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    
    class Meta:
        model = OfferView
        fields = [
            'id', 'offer', 'offer_name', 'client', 'client_name',
            'viewed_at', 'clicked', 'clicked_at'
        ]


class OfferCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear ofertas (admin)"""
    class Meta:
        model = Offer
        fields = [
            'name', 'description', 'offer_type', 'discount_value',
            'discount_type', 'banner_image', 'cta_text', 'start_date',
            'end_date', 'products', 'min_purchase', 'max_uses',
            'target_all', 'target_first_time', 'target_repeat',
            'min_visits', 'show_on_splash', 'send_whatsapp',
            'whatsapp_delay_minutes'
        ]


class CouponSerializer(serializers.ModelSerializer):
    offer_name = serializers.CharField(source='offer.name', read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'offer', 'offer_name', 'discount', 'discount_type',
            'max_uses', 'uses_count', 'valid_from', 'valid_until', 'is_active', 'is_valid'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'client', 'client_name', 'offer', 'coupon', 'amount',
            'flow_token', 'status', 'created_at', 'updated_at'
        ]
