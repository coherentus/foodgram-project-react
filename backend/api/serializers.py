from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from logic.models import FavourRecipe, Follow
from recipes.models import Component, Product, Recipe, Tag
from users.models import CustomUser


class TagSerializer(serializers.ModelSerializer):
    """Serializer Tag model."""
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    color = serializers.CharField(max_length=7)
    slug = serializers.SlugField(max_length=200)

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('id', 'name', 'color', 'slug')


class ProductSerializer(serializers.ModelSerializer):
    """Serializer Product model."""
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    measurement_unit = serializers.CharField(max_length=200)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id', )


class ComponentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='product.id')
    name = serializers.ReadOnlyField(source='product.name')
    measurement_unit = serializers.ReadOnlyField(
        source='product.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:

        model = Component
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = (
            UniqueTogetherValidator(
                queryset=Component.objects.all(),
                fields=('product', 'recipe')
            ),
        )
        read_only_fields = ('id', )


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer CustomUser model."""
    email = serializers.EmailField(max_length=254, allow_blank=False)
    username = serializers.CharField(max_length=150, allow_blank=False)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """Return True if request.user subscribed to author."""
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        if user and user.is_authenticated:
            return Follow.objects.filter(user=user, author=obj.id).exists()
        return False


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer Recipe model."""
    author = CustomUserSerializer(read_only=True)
    name = serializers.CharField(source='title')
    image = Base64ImageField(
        source='picture',
        max_length=None, use_url=True
    )
    ingredients = ComponentSerializer(
        many=True, read_only=True, source='recipe_components'
    )
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
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
            return obj.favourite.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.get_user()
        if user and user.is_authenticated:
            return obj.basket_recipes.filter(user=user).exists()
        return False

    def validate_tags(self, data):
        if not data:
            raise serializers.ValidationError(
                'Ошибка: Создание рецепта без тега невозможно'
            )

        if len(data) != len(set(data)):
            raise serializers.ValidationError(
                'Ошибка: Тег для рецепта указывается единожды'
            )

        for tag_id in data:
            if not Tag.objects.filter(id=tag_id).exists():
                raise serializers.ValidationError(
                    f'Ошибка: Тега с указанным id = {tag_id} не существует'
                )
        return data

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Ошибка: Невозможно создание рецепта без ингредиента'
            )

        ingr_ids = [component['id'] for component in ingredients]
        if len(ingr_ids) != len(set(ingr_ids)):
            raise serializers.ValidationError(
                'Ошибка: Ингредиент для рецепта указывается единожды'
            )
        for ingrdnt_id in ingr_ids:
            if not Product.objects.filter(id=ingrdnt_id).exists():
                raise serializers.ValidationError(
                    'Ошибка: Ингредиента '
                    f'с указанным id = {ingrdnt_id} не существует'
                )

        amounts = [item['amount'] for item in ingredients]
        for amount in amounts:
            if not isinstance(amount, int) or amount < 1:
                raise serializers.ValidationError(
                    'Ошибка: Минимальное значение количества '
                    'ингредиента: 1'
                )
        data['ingredients'] = ingredients
        return data

    def validate_cooking_time(self, value):
        if not isinstance(value, int) or value < 1:
            raise serializers.ValidationError(
                'Ошибка: Минимальное значение времени приготовления '
                '1 минута'
            )
        return value

    def validate(self, data):
        author = self.context.get('request').user
        if self.context.get('request').method == 'POST':
            name = data.get('name')
            if Recipe.objects.filter(author=author, title=name).exists():
                raise serializers.ValidationError(
                    f'Ошибка: У автора - {author.username} уже есть рецепт '
                    f'с названием {name}'
                )
        data['author'] = author
        return data

    def create_recipe_components(self, ingredients, recipe):
        for ingredient in ingredients:
            Component.objects.create(
                recipe=recipe,
                product_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
        return recipe

    def create(self, validated_data):
        if not self.is_valid():
            raise serializers.ValidationError('Данные не валидны')
        components = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        
        # tags = self.initial_data.get('tags')
        # components = self.initial_data.get('ingredients')
        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)
            self.create_recipe_components(components, recipe)
            recipe.tags.set(tags)
        return recipe

    def update(self, recipe, validated_data):
        if not self.is_valid():
            raise serializers.ValidationError('Данные не валидны')
        tags = self.validated_data.pop('tags')
        components = self.validated_data.pop('ingredients')
        # tags = self.initial_data.get('tags')
        # components = self.initial_data.get('ingredients')
        with transaction.atomic():
            recipe = super().update(recipe, validated_data)
            recipe.components.clear()
            recipe.tags.clear()
            self.create_recipe_components(components, recipe)
            recipe.tags.set(tags)
        return recipe


class RecipeShowSerializer(serializers.ModelSerializer):
    """Return short list of fields."""
    name = serializers.CharField(source='title')
    image = Base64ImageField(max_length=None, use_url=True, source='picture')

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class FavouriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        required=False
    )
    recipe = serializers.SlugRelatedField(
        slug_field='recipe_id', read_only=True,
        required=False
    )

    class Meta:
        model = FavourRecipe
        fields = ('user', 'recipe')

    def validate(self, data):
        user = self.context['request'].user
        recipe_id = self.context.get('view').kwargs.get('recipe_id')

        if FavourRecipe.objects.filter(
            user=user.id, recipe=recipe_id
        ).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в избранном.')
        return data


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        source='author.email',
        required=False
    )
    id = serializers.IntegerField(
        source='author.id',
        required=False
    )
    username = serializers.CharField(
        source='author.username',
        required=False
    )
    first_name = serializers.CharField(
        source='author.first_name',
        required=False
    )
    last_name = serializers.CharField(
        source='author.last_name',
        required=False
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        is_subscribed = Follow.objects.filter(
            user=obj.user, author=obj.author).exists()
        return is_subscribed

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_per_user = None
        if 'recipes_limit' in request.query_params:
            recipes_per_user = int(request.query_params['recipes_limit'])
        queryset = Recipe.objects.filter(
            author=obj.author
        )[:recipes_per_user]
        serializer = RecipeShowSerializer(queryset, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()
