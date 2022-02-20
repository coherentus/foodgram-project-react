from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from logic.models import FavourRecipe, Follow
from recipes.models import Component, Product, Recipe, Tag
from users.models import CustomUser


class TagSerializer(serializers.ModelSerializer):
    """Serializer Tag model."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200, read_only=True)
    color = serializers.CharField(max_length=7, read_only=True)
    slug = serializers.SlugField(max_length=200, read_only=True)

    class Meta:
        model = Tag
        fields = '__all__'
        # read_only_fields = ('id', 'name', 'color', 'slug')


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


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = ('id', 'amount',
                  # recipe', 'product'
            )
        extra_kwargs = {
            'id': {
                'read_only': False, }}
        """        'error_messages': {
                    'does_not_exist': INGREDIENT_DOES_NOT_EXIST,
                }
            },
            'amount': {
                'error_messages': {
                    'min_value': INGREDIENT_MIN_AMOUNT_ERROR.format(
                        min_value=INGREDIENT_MIN_AMOUNT
                    ),
                }
            }
        }"""


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Serializer for write Recipe model instance."""
    name = serializers.CharField(source='title')
    image = Base64ImageField(
        source='picture',
        max_length=None, use_url=True
    )
    # ingredients = ComponentSerializer(many=True, source='components')  # RecipeIngredientWriteSerializer
    tags = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field='id',
            queryset=Tag.objects.all(),
        ),
    )


    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',
        )
        """extra_kwargs = {
            'cooking_time': {
                'error_messages': {
                    'min_value': COOKING_TIME_MIN_ERROR,
                }
            }
        }"""
        
    def validate(self, data):
        if data['cooking_time'] < 1:
            raise serializers.ValidationError(
                'Ошибка: Минимальное значение времени приготовления '
                '1 минута'
            )
        
        if not data['tags']:
            raise serializers.ValidationError(
                'Ошибка: Создание рецепта без тега невозможно'
            )
        if len(data['tags']) != len(set(data['tags'])):
            raise serializers.ValidationError(
                'Ошибка: Тег для рецепта указывается единожды'
            )

        for tag in data['tags']:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    f'Ошибка: Тега с указанным id = {tag.id} не существует'
                )
        
        
        if len(data['components']) == 0:
            raise serializers.ValidationError(
                'Ошибка: Невозможно создание рецепта без ингредиента'
            )
        compnt_ids = []
        for component in data['components']:
            cur_id, cur_amount = component['id'], component['amount']
            if not Product.objects.filter(id=cur_id).exists():
                raise serializers.ValidationError(
                    'Ошибка: Ингредиента '
                    f'с указанным id = {cur_id} не существует')
            compnt_ids.append(cur_id)
            if int(cur_amount) < 1:
                raise serializers.ValidationError(
                    'Ошибка: Минимальное количество ингредиента: 1')
        if len(compnt_ids) != len(set(compnt_ids)):
            raise serializers.ValidationError(
                'Ошибка: Ингредиент для рецепта указывается единожды'
            )

        return data

    def add_components_and_tags(self, recipe, validated_data):
        components, tags = (
            validated_data.pop('components'), validated_data.pop('tags')
        )
        for component in components:
            _, created = Component.objects.get_or_create(
                product=get_object_or_404(Product, id=component['id']),
                amount=component['amount'],
                recipe=recipe
            )
            if not created:
                raise serializers.ValidationError(
                    'Ошибка: Ингредиент для рецепта указывается единожды'
                )
            # recipe.components.add(recipe_component)
        recipe.tags.set(tags)
        return recipe

    def create(self, validated_data):
        saved = {}
        saved['components'] = validated_data.pop('components')
        saved['tags'] = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        return self.add_components_and_tags(recipe, saved)

    def update(self, instance, validated_data):
        instance.components.clear()
        instance.tags.clear()
        instance = self.add_components_and_tags(instance, validated_data)
        return super().update(instance, validated_data)

    """author = CustomUserSerializer(read_only=True)
    name = serializers.CharField(source='title')
    image = Base64ImageField(
        source='picture',
        max_length=None, use_url=True
    )
    # ingredients = RecipeIngredientWriteSerializer(many=True)

    # ingredients payload from request [{'id': int, 'amount': int},]
    ingredients = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())

    )
    tags = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field='id',
            queryset=Tag.objects.all(),
        ),
    )

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    # tags payload from request [int,]
    tags = TagSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    tags = serializers.ListField(
        child=serializers.IntegerField()
    )

    class Meta:
        model = Recipe
        fields = (
            # 'id',
            'tags', 'author',
            'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    def validate_cooking_time(self, value):
        if not isinstance(value, int) or value < 1:
            raise serializers.ValidationError(
                'Ошибка: Минимальное значение времени приготовления '
                '1 минута'
            )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Ошибка: Создание рецепта без тега невозможно'
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Ошибка: Тег для рецепта указывается единожды'
            )

        for tag_id in value:
            if not Tag.objects.filter(id=tag_id.id).exists():
                raise serializers.ValidationError(
                    f'Ошибка: Тега с указанным id = {tag_id} не существует'
                )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Ошибка: Невозможно создание рецепта без ингредиента'
            )

        compnt_ids = []
        for component in value:
            cur_id, cur_amount = component['id'], component['amount']
            if not Product.objects.filter(id=cur_id).exists():
                raise serializers.ValidationError(
                    'Ошибка: Ингредиента '
                    f'с указанным id = {cur_id} не существует')
            compnt_ids.append(cur_id)
            if int(cur_amount) < 1:
                raise serializers.ValidationError(
                    'Ошибка: Минимальное количество ингредиента: 1')
        if len(compnt_ids) != len(set(compnt_ids)):
            raise serializers.ValidationError(
                'Ошибка: Ингредиент для рецепта указывается единожды'
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
        components = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)
            self.create_recipe_components(components, recipe)
            recipe.tags.set(tags)
        return recipe

    def update(self, recipe, validated_data):
        tags = self.validated_data.pop('tags')
        components = self.validated_data.pop('ingredients')
        with transaction.atomic():
            recipe = super().update(recipe, validated_data)
            recipe.components.clear()
            recipe.tags.clear()
            self.create_recipe_components(components, recipe)
            for tag in tags:
                recipe.tags.add(Tag.objects(id=tag))
            recipe.tags.set(tags)
        return recipe"""


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class RecipeReadSerializer(DynamicFieldsModelSerializer):
    """Return dynamical list of fields."""
    name = serializers.CharField(source='title')
    image = Base64ImageField(max_length=None, use_url=True, source='picture')
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(
        source='picture',
        max_length=None, use_url=True
    )
    ingredients = ComponentSerializer(
        many=True, source='recipe_components',
        read_only=True
    )
    tags = TagSerializer(many=True)
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

    recipe_fields = ('id', 'name', 'image', 'cooking_time')

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
        serializer = RecipeReadSerializer(queryset, many=True,
                                          fields=self.recipe_fields)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()
