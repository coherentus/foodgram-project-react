class RecipeReadSerializer(serializers.ModelSerializer):
    """Serializer Recipe model for 'api/recipe/' -list endpoint."""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = ComponentSerializer(
        source='components',
        many=True,
        read_only=True,
    )
    name = serializers.CharField(source='title')
    image = Base64ImageField(max_length=None, use_url=True, source='picture')
        
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_user(self):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        return user

    def get_is_favorited(self, obj):
        user = self.get_user()
        if user and user.is_authenticated:
            return obj.favourite.filter(user=user.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.get_user()
        if user and user.is_authenticated:
            return obj.bascket_recipes.filter(user=user.id).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = ComponentSerializer(many=True)
    tags = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field='id',
            queryset=Tag.objects.all(),
        ),
    )
    name = serializers.CharField(source='title')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',
        )

    def validate(self, data):
        components = self.initial_data.get('ingredients')
        if not components:
            raise serializers.ValidationError({
                'ingredients': 'Ошибка. В рецепте должен быть '
                'хотя бы один компонент.'
                })
        components_values = []
        for component_item in components:
            component = get_object_or_404(Component,
                                           id=component_item['id'])
            if component in components_values:
                raise serializers.ValidationError(
                    'Ошибка. Дублирование компонентов рецепта '
                    'не допускается.'
                )
            components_values.append(component)
            if int(component_item['amount']) < MIN_AMOUNT_VALUE:
                raise serializers.ValidationError({
                    'ingredients': MIN_AMOUNT_MESSAGE
                })
        data['ingredients'] = components
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) < MIN_COOKING_VALUE:
                raise serializers.ValidationError({
                    'cooking_time': MIN_COOKING_MESSAGE
                })
        return data

    def create_components(self, components, recipe):
        for component in components:
            Component.objects.create(
                recipe=recipe,
                product_id=component.get('id'),
                amount=component.get('amount'),
            )

    def create(self, validated_data):
        image = validated_data.pop('image')
        components_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        tags_data = self.initial_data.get('tags')
        recipe.tags.set(tags_data)
        self.create_components(components_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        Component.objects.filter(recipe=instance).all().delete()
        self.create_components(validated_data.get('ingredients'), instance)
        instance.save()
        return instance