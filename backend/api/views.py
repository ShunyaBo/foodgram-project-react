from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError


from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPagePagination
from api.permissions import IsAuthorAdmin
from api.serializers import (FavoriteShoppingCartSerializer,
                             FollowerSerializer,
                             IngredientSerializer,
                             RecipeGetSerializer,
                             RecipeCreateSerializer,
                             TagSerializer,
                             UserSerializer)
from recipes.models import (FavoriteRecipe, Ingredient,
                            Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import User, Follower


class TagViewSet(ReadOnlyModelViewSet):
    """
    Получение списков тегов и информации о теге по id.
    Создание и редактирование тегов доступно только в админ-панеле.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    Получение списка ингредиентов, информации об ингредиенте по id.
    Создание и редактирование ингредиентов доступно только в админ-панеле.
    Доступен поиск по частичному вхождению в начале названия ингредиента.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.UpdateModelMixin,
                    GenericViewSet):
    """
    Получение списка рецептов, информации о рецепте по id,
    создание/частичное изменение/удаление рецепта по id.
    Изменять рецепт может только автор или админ.
    В списоке рецептов доступна фильтрация по избранному, автору,
    списку покупок и тегам.

    Добавление/удаление рецептов в избранное и список покупок
    для авторизованных пользователей.
    Отправка файла со списком рецептов.
    """

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorAdmin,)
    pagination_class = LimitPagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    lookup_field = 'id'

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от метода."""
        if self.action == "list" or self.action == "retrieve":
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, id):
        """Добавление/удаление в список покупок"""
        user = get_object_or_404(User, username=request.user)
        recipe = get_object_or_404(Recipe, id=id)
        if self.request.method == "POST":
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    "Повтороное добавление",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                ShoppingCart.objects.create(user=user, recipe=recipe)
            except IntegrityError as error:
                if "unique constraint" in error.args:
                    return Response(
                        "Повтороное добавление",
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            serializer = FavoriteShoppingCartSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_200_OK)
        try:
            recipe_in_cart = ShoppingCart.objects.get(user=user, recipe=recipe)
        except ObjectDoesNotExist:
            return Response(
                "Попытка не существующего удаления",
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe_in_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, id):
        """Добавление/удаление в избранное"""
        user = get_object_or_404(User, username=request.user)
        recipe = get_object_or_404(Recipe, id=id)
        if self.request.method == "POST":
            if FavoriteRecipe.objects.filter(user=user,
                                             recipe=recipe).exists():
                return Response(
                    "Повтороное добавление!!!", status=status.HTTP_400_BAD_REQUEST
                )
            try:
                FavoriteRecipe.objects.create(user=user, recipe=recipe)
            except IntegrityError as error:
                if "unique constraint" in error.args:
                    return Response(
                        "Попытка повторного добавления!!!",
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            serializer = FavoriteShoppingCartSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_200_OK)
        try:
            favorite = FavoriteRecipe.objects.get(
                user=user,
                recipe=recipe,
            )
        except ObjectDoesNotExist:
            return Response(
                "Попытка не существующего удаления!!!",
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    # @staticmethod
    # def method_post(request, model, user, id):
    #     """
    #     Вспомогательный метод POST(добавление в список) для методов:
    #     def favorite и shopping_cart.
    #     """
    #     recipe = get_object_or_404(Recipe, id=id)
    #     model.objects.create(user=user, recipe=recipe)
    #     data = {'user': user, 'recipe': recipe}
    #     serializer = FavoriteShoppingCartSerializer(
    #         data=data,
    #         context={'request': request})
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(data=serializer.data,
    #                         status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors,
    #                     status=status.HTTP_400_BAD_REQUEST)

    # @staticmethod
    # def method_delete(request, model, user, id, error_message):
    #     """
    #     Вспомогательный метод DELETE(удаление из списка) для методов:
    #     def favorite и shopping_cart.
    #     """
    #     # user = request.user
    #     recipe = get_object_or_404(Recipe, id=id)
    #     if not model.objects.filter(user=user, recipe=recipe).exists():
    #         return Response({'errors': error_message},
    #                         status=status.HTTP_400_BAD_REQUEST)
    #     get_object_or_404(model, user=user, recipe=recipe).delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(methods=('post', 'delete'),
    #         detail=True,
    #         permission_classes=[IsAuthenticated],)
    # def favorite(self, request, id):
    #     """Добавление/удаление рецепта в избранное."""
    #     user = get_object_or_404(User, username=request.user)
    #     if request.method == 'POST':
    #         return self.method_post(request, FavoriteRecipe, user, id)
    #     else:
    #         error_message = ('Вы пытаетесь удалить рецепт,'
    #                          'которого нет у Вас в избранном')
    #         return self.method_delete(request, FavoriteRecipe, user,
    #                                   id, error_message)

    # @action(methods=('post', 'delete'),
    #         detail=True,
    #         permission_classes=[IsAuthenticated],)
    # def shopping_cart(self, request, id):
    #     """Добавление/удаление рецепта в список покупок."""
    #     user = get_object_or_404(User, username=request.user)
    #     if request.method == 'POST':
    #         return self.method_post(request, ShoppingCart, user, id)
    #     else:
    #         error_message = ('Вы пытаетесь удалить рецепт,'
    #                          'которого нет у Вас в cписке покупок')
    #         return self.method_delete(request, ShoppingCart,
    #                                   id, error_message)

    @action(methods=('get'),
            detail=False,
            permission_classes=[IsAuthenticated],)
    def download_shopping_cart(self, request):
        """Создаем список покупок и скачиваем файл со списком покупок."""
        user = request.user
        shopping_dict = RecipeIngredient.objects.filter(
            recipes__shopping_cart___user=user).values(
                'ingredient__name',
                'ingredient__measurement_unit').annotate(
                    amount=Sum('amount'))
        shopping_list = list()
        shopping_list.append('Список покупок:\n')
        for item in shopping_dict:
            shopping_list.append(
                f'{item} - ({shopping_dict[item]["measurement_unit"]}) - '
                f'{shopping_dict[item]["amount"]} \n')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="yourlist.txt"'
        return response


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    pagination_class = LimitPagePagination

    lookup_field = 'id'

    @action(methods=('get',),
            detail=False,
            permission_classes=[IsAuthenticated],)
    def me(self, request):
        """Получение пользователем данных о себе (users/me)."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('id'))
        serializer = self.get_serializer(user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=('post', 'delete',),
            detail=True,
            permission_classes=[IsAuthenticated],)
    def subscribe(self, request, id):
        """Подписаться/отписаться."""
        user = get_object_or_404(User, username=request.user)
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if user == author:
                return Response({'message': 'Вы хотите подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follower.objects.create(user=user, author=author,)
            serializer = FollowerSerializer(author,
                                            context={"request": request},)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            author_del = Follower.objects.filter(user=user, author=author,)
            if author_del.exists():
                author_del.delete()
                return Response({'message': 'Вы отписались от автора'},
                                status=status.HTTP_204_NO_CONTENT)

    @action(methods=('get',),
            detail=False,
            permission_classes=[IsAuthenticated],)
    def subscriptions(self, request, *args, **kwargs):
        """Получение списка всех подписок на пользователей."""
        user = get_object_or_404(User, username=request.user)
        following = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(following)
        if pages is not None:
            serializer = FollowerSerializer(
                pages, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(pages, many=True)
        return Response(serializer.data)
