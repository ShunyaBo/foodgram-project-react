import base64

from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (FavoriteRecipe, Ingredient,
                            Recipe, RecipeIngredient,
                            ShoppingCart, Tag)

from users.models import User, Follower


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        user = self.context['request'].user

        if user.is_authenticated:
            return Follower.objects.filter(user=user, author=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов в рецепте.
    При GET запросах - Получение рецепта/списка рецептов.
    """

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientChangeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов в рецепте.
    При POST и PATCH запросе - создание/обновление рецепта.
    """
    id = serializers.IntegerField()
    amount = serializers.IntegerField()
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['name'] =
    #     data['measurement_unit'] =
    #     return data

    # class Meta:
    #     model = RecipeIngredient
    #     fields = ('id', 'name', 'measurement_unit', 'amount')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')
        validators = (
            UniqueTogetherValidator(
                queryset=RecipeIngredient.objects.all(),
                fields=('ingredient', 'recipe')
            )
        )

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиентов должно быть больше 1'
            )
        return value


class RecipeGetSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения информации о рецепте ("list", "retrieve").
    GET-запросы на получение списка рецептов, получение рецепта.
    """
    image = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientInRecipeSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',  'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('id', 'author', 'tags', 'ingredients')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.favorite.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.shopping_cart.filter(user=user).exists()
        return False

    def get_image(self, obj):
        return f"{settings.MEDIA_URL}{obj.image}"


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания/обновления рецепта.
    """
    author = UserSerializer()
    ingredients = IngredientChangeSerializer(many=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient,
                                             id=ingredient['id']),
                amount=ingredient['amount'])
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        for ingredient in ingredients:
            RecipeIngredient.objects.update_or_create(
                    recipe=instance,
                    ingredient=get_object_or_404(Ingredient,
                                                 id=ingredient['id']),
                    amount=ingredient['amount'])
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance=instance, context=self.context).data

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',  'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('id', 'author', 'tags', 'ingredients')


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Вспомогательный сериализатор для добавления рецепта в избранное.
    POST-запросов на api/recipes/{id}/favorite/ и
    на /api/recipes/{id}/shopping_cart/.
    """
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return f"{settings.MEDIA_URL}{obj.image}"

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с избранными рецептами."""
    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShortRecipeSerializer(instance.recipe,
                                     context={'request': request}).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShortRecipeSerializer(instance.recipe,
                                     context={'request': request}).data
# class FollowerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Follower
#         fields = ('user', 'author')


class FollowerSerializer(serializers.ModelSerializer):
    """"Сериализатор,предоставляющий информацию о подписках пользователя."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name',
                            'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True,
                                     context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
