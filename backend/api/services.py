from django.contrib.auth import get_user_model
from django.db.models import Model, Subquery
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.http import Http404

from users.models import UserSubs
from food.models import RecipeIngredient, RecipeTag, Ingredient, Recipe
from api.exceptions import (
    AlreadySubscribedError,
    NotSubscribedError,
    SelfSubscriptionError
)


User = get_user_model()


def get_all_objects(model: Model) -> QuerySet:
    return model.objects.all()


def subscribe(user: User, sub: User) -> QuerySet:
    if user.id == sub.id:
        raise SelfSubscriptionError
    if UserSubs.objects.filter(user_id=user.id, sub_id=sub.id).exists():
        raise AlreadySubscribedError
    return UserSubs.objects.get_or_create(user_id=user, sub_id=sub)


def unsubscribe(user_id: int, sub_id: int) -> QuerySet:
    user = get_object_or_404(User, id=user_id)
    sub = get_object_or_404(User, id=sub_id)
    try:
        get_object_or_404(UserSubs, user_id=user, sub_id=sub).delete()
    except Http404:
        raise NotSubscribedError


def get_subs_ids(user_id: int) -> list[tuple[int]]:
    return UserSubs.objects.filter(
        user_id=user_id).values_list('sub_id', flat=True)


def get_subscriptions(user_id: int) -> QuerySet:
    subs = UserSubs.objects.filter(user_id=user_id).values('sub_id')
    return User.objects.filter(id__in=Subquery(subs))


def get_recipe_ingredients(recipe_id: int) -> QuerySet:
    return Ingredient.objects.prefetch_related(
        'recipe_ingredient').filter(recipe_ingredient__recipe_id=recipe_id)


def get_ingredient_amount(recipe_id: int, ingredient_id: int) -> int:
    return int(get_object_or_404(
        RecipeIngredient,
        recipe_id=recipe_id,
        ingredient_id=ingredient_id
    ).amount)


def get_available_ids(model: Model) -> list[int]:
    return model.objects.all().values_list('id', flat=True)


def add_ingredients_to_recipe(
        edit: bool,
        recipe: Recipe,
        ingredients_amounts: list[dict[str, int]]) -> None:
    if edit:
        RecipeIngredient.objects.filter(recipe_id=recipe.id).delete()

    for ingredient in ingredients_amounts:
        RecipeIngredient.objects.get_or_create(
            recipe_id=recipe,
            ingredient_id=Ingredient.objects.get(id=ingredient['id']),
            amount=ingredient['amount']
        )


def add_tags_to_recipe(edit: bool,
                       recipe: Recipe,
                       tags_ids: list[int]) -> None:
    if edit:
        RecipeTag.objects.filter(recipe_id=recipe.id).delete()

    for tag_id in tags_ids:
        RecipeTag.objects.get_or_create(
            recipe_id=recipe.id,
            tag_id=tag_id
        )


def create_recipe(author_id: int,
                  ingredients: list[dict[str, int]],
                  tags_ids: list[int],
                  **kwargs) -> Recipe:
    recipe_instance = Recipe.objects.create(
        author_id=author_id,
        **kwargs
    )

    add_ingredients_to_recipe(False, recipe_instance, ingredients)
    add_tags_to_recipe(False, recipe_instance, tags_ids)

    return recipe_instance
