from rest_framework import serializers


from users.models import User, Follower
from recipes.models import (FavoriteRecipe, Ingredient,
                            Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user

        if user.is_authenticated:
            return Follower.objects.filter(user=user, author=obj).exists()
        return False


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = ('user', 'author')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('name', 'author', 'text', 'image', 'tags',
                  'ingredients', 'cooking_time', 'pub_date')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ('recipe', 'ingredient', 'amount')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
