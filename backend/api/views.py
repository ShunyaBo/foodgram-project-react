from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)

from api.filters import RecipeFilter
from api.permissions import IsAdminAuthor
from api.serializers import (FavoriteRecipeSerializer, FollowerSerializer,
                             IngredientSerializer, RecipeGetSerializer,
                             RecipeCreateSerializer, ShoppingCartSerializer,
                             TagSerializer, UserSerializer)
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
    filter_backends = (filters.SearchFilter)
    search_fields = ('name',)
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
    permission_classes = (IsAdminAuthor,)
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от метода."""
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def method_delete(self, request, model, instance, error_message):
        """Вспомогательный метод для методов: def favorite и shopping_cart."""
        user = request.user
        if not model.objects.filter(user=user, recipe=instance).exists():
            return Response({'errors': error_message},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.filter(user=user, recipe=instance).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],)
    def favorite(self, request, pk):
        """Добавление/удаление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            data = {'user': request.user.pk, 'recipe': recipe.pk}
            serializer = FavoriteRecipeSerializer(data=data,
                                                  сontext={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            error_message = 'У Вас нет этого рецепта в избранном'
            return self.method_delete(request, FavoriteRecipe,
                                      recipe, error_message)
            # if not FavoriteRecipe.objects.filter(user=request.user,
            #                                      recipe=recipe
            #                                      ).exists():
            #     return Response({'errors': error_message},
            #                     status=status.HTTP_400_BAD_REQUEST)
            # FavoriteRecipe.objects.filter(user=request.user,
            #                               recipe=recipe).delete()
            # return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],)
    def shopping_cart(self, request, pk):
        """Добавление/удаление рецепта в список покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            data = {'user': request.user.pk, 'recipe': recipe.pk}
            serializer = ShoppingCartSerializer(data=data,
                                                context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            error_message = 'У Вас нет этого рецепта в cписке покупок'
            return self.method_delete(request, ShoppingCart,
                                      recipe, error_message)
            error_message = 'У вас нет этого рецепта в cписке покупок'
            # if not ShoppingCart.objects.filter(user=request.user,
            #                                      recipe=recipe
            #                                      ).exists():
            #     return Response({'errors': error_message},
            #                     status=status.HTTP_400_BAD_REQUEST)
            # ShoppingCart.objects.filter(user=request.user,
            #                               recipe=recipe).delete()
            # return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated],)
    def download_shopping_cart(self, request):
        """Скачать файл со списком покупок."""
        user = request.user
        shopping_list = user.shopping_cart.all()
        shopping_dict = {}
        for record in shopping_list:
            recipe = record.recipe
            ingredients = RecipeIngredient.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                amount = ingredient.amount
                name = ingredient.name
                measurement_unit = ingredient.measurement_unit
                if name not in shopping_dict:
                    shopping_dict[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount}
                else:
                    shopping_dict[name]['amount'] = (
                            shopping_dict[name]['amount'] + amount)
        shoppinglist = list()
        shoppinglist.append('Список покупок:\n\n')
        for item in shopping_dict:
            shoppinglist.append(
                f'{item} ({shopping_dict[item]["measurement_unit"]}) - '
                f'{shopping_dict[item]["amount"]} \n')
        shoppinglist.append('\n')
        shoppinglist.append('Продуктовый помощник Foodgram ©')
        response = HttpResponse(shoppinglist, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response


class FollowViewSet(mixins.ListModelMixin, GenericViewSet):
    """Получение списка всех подписок на пользователей."""
    serializer_class = FollowerSerializer

    def get_queryset(self):
        return Follower.objects.filter(user=self.request.user)


class SubscribeViewSet(mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       GenericViewSet):
    """Подписаться/отписаться от пользователя"""
    serializer_class = FollowerSerializer

    def perform_create(self, serializer):
        author = get_object_or_404(User, pk=self.kwargs.get('id'))
        serializer.save(user=self.request.user, author=author)

    def delete(self, request, *args, **kwargs):
        author = get_object_or_404(User, pk=self.kwargs.get('id'))
        follower = get_object_or_404(Follower,
                                     user=self.request.user,
                                     author=author)
        follower.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['id'] = int(self.kwargs.get('id'))
        return context


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination

    lookup_field = 'id'

    @action(detail=False,
            methods=('get',),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Получение пользователем данных о себе."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('id'))
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
