import base64

from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (FavoriteRecipe, Ingredient,
                            Recipe, RecipeIngredient,
                            Tag)

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

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')
        validators = (
            UniqueTogetherValidator(
                queryset=RecipeIngredient.objects.all(),
                fields=('ingredient', 'recipe')
            )
        )


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
            return FavoriteRecipe.objects.filter(user=user,
                                                 recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.shopping_cart.filter(user=user, recipe=obj).exists()
        return False

    def get_image(self, obj):
        return f"{settings.MEDIA_URL}{obj.image}"


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания/обновления рецепта.
    """
    author = UserSerializer()
    ingredients = IngredientChangeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def recipe_ingredients_amount(self, recipes, tags_data, ingredients_data):
        """
        Вспомогательная функция для записи ингредиентов
        и их количества в рецепт.
        """
        recipes.tags.set(tags_data)
        ingredient_amounts = []
        for item in ingredients_data:
            ingredient = item.get('ingredient')
            amount = item.get('amount')
            ingredient_amount, _ = RecipeIngredient.objects.get_or_create(
                ingredient=ingredient,
                amount=amount,
            )
            ingredient_amounts.append(ingredient_amount)
        recipes.ingredients.set(ingredient_amounts)
        return recipes

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data)
        return self.recipe_ingredients_amount(
            recipe, tags, ingredients
        )

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        instance.ingredients.clear()
        instance.tags.clear()

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return self.recipe_ingredients_amount(
            instance, tags, ingredients
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return FavoriteRecipe.objects.filter(user=user,
                                                 recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.shopping_cart.filter(user=user,
                                            recipe=obj).exists()
        return False

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',  'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('id', 'author', 'tags', 'ingredients')


class FavoriteShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода рецептов в избранном и списке покупок."""
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    # """
    # Вспомогательный сериализатор для добавления рецепта в избранное.
    # POST-запросов на api/recipes/{id}/favorite/ и
    # на /api/recipes/{id}/shopping_cart/.
    # """
    # image = serializers.SerializerMethodField()
    # # name = написать http://127.0.0.1:8000/api/recipes/1/shopping_cart/ post
    # # cooking_time = написать Field name `name` is not valid for model `RecipeIngredient`.

    # def get_image(self, obj):
    #     return f'{settings.MEDIA_URL}{obj.image}'

    # class Meta:
    #     model = RecipeIngredient
    #     fields = ('id', 'name', 'image', 'cooking_time')


# class FavoriteRecipeSerializer(serializers.ModelSerializer):
#     """Сериализатор для работы с избранными рецептами."""
#     class Meta:
#         model = FavoriteRecipe
#         fields = ('user', 'recipe')

#     def to_representation(self, instance):
#         request = self.context.get('request')
#         return ShortRecipeSerializer(instance.recipe,
#                                      context={'request': request}).data


# class ShoppingCartSerializer(serializers.ModelSerializer):
#     """Сериализатор для работы со списком рецептов."""
#     class Meta:
#         model = ShoppingCart
#         fields = ('user', 'recipe')

#     def to_representation(self, instance):
#         request = self.context.get('request')
#         return ShortRecipeSerializer(instance.recipe,
#                                      context={'request': request}).data


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

    def get_is_subscribed(self, obj):
        return Follower.objects.filter(user=obj.user,
                                       author=obj.author).exists()

    # def get_recipes(self, obj):
    #     request = self.context.get('request')
    #     recipes_limit = None
    #     if request:
    #         recipes_limit = request.query_params.get('recipes_limit')
    #     recipes = obj.recipe_author.all()
    #     if recipes_limit:
    #         recipes = obj.recipe_author.all()[:int(recipes_limit)]
    #     return FavoriteShoppingCartSerializer(
    #         recipes, many=True,
    #         context={'request': request}).data

    def get_recipes(self, obj):
        limit = self.context["request"].query_params.get("recipes_limit")
        query = obj.recipe_author.all()
        if limit:
            query = query[: int(limit)]
        recipes = FavoriteShoppingCartSerializer(query, many=True)
        return recipes.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
