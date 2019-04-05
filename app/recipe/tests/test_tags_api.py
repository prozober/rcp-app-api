from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the public available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Testing that login is required for retriving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@admin.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)
        print(res)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def tags_limited_to_user(self):
        """Test that tags returned are fot the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'test1@admin.com',
            'password123'
        )

        Tag.objects.create(name='Fruity', user=user2)
        tag = Tag.objects.create(name='Comfort Food', user=self.user)

        res = self.cient.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Testing the tag are created successfully"""
        payload = {'name': 'Test Tag'}

        res = self.client.post(TAGS_URL, payload)

        exits = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        )

        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(exits.count(), 1)

    def test_create_tag_invalid(self):
        """Testing the tag is not created when name is invalid"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
