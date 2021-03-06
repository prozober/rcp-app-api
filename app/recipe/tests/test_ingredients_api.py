from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsAPITest(TestCase):
    """Testing the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Tests that the login is required to access the API"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITest(TestCase):
    """Testing the ingredients authorized API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@admin.com',
            'password123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """Test listing the ingredients"""
        Ingredient.objects.create(user=self.user, name='Sugar')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test listing the ingredients are listing for the authorized user"""
        user2 = get_user_model().objects.create_user(
            'test1@admin.com',
            'password123'
        )

        ingredient = Ingredient.objects.create(user=self.user, name='Salt')
        Ingredient.objects.create(user=user2, name='Sugar')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Testing the ingredients are created successfully"""

        payload = {'name': 'Sugar'}

        res = self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Testing the invalid creation when no name is provided"""

        payload = {'name': ''}

        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipe(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Salt')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Rice')

        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Plain Rice',
            time_minutes=20,
            price=2.00
        )

        recipe1.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Testing filtering ingredients by assigned returns unique items"""
        ingredient = Ingredient.objects.create(user=self.user, name='Salt')
        Ingredient.objects.create(user=self.user, name='Rice')

        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Plain Rice',
            time_minutes=20,
            price=2.00
        )

        recipe1.ingredients.add(ingredient)

        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Rice spiced',
            time_minutes=20,
            price=2.00
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
