class ObrazSerializer(serializers.ModelSerializer):
    goods = serializers.JSONField()
    class Meta:
        model = Obraz
        fields = ('datum_isteka', 'e_mail', 'adress', 'taxes',
                  'order_num','goods', 'store_user',)