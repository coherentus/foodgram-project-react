import json
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse

from recipes.models import Tag
from ..serializers import TagSerializer

client = Client()


class GetAllTagTest(TestCase):
    """ Test module for GET all tags API """
    def setUp(self):
        Tag.objects.create(
            name='Casper', color='3', slug='Bull Dog')
        Tag.objects.create(
            name='Muffin', color='Brown', slug='Gradane')
        Tag.objects.create(
            name='Rambo', color='Labrador', slug='Black')
        Tag.objects.create(
            name='Ricky', color='Labrador2', slug='Brown2')

    def test_get_all_tags(self):
        # get API response
        response = client.get(reverse('tags-list'))
        # get data from db
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetSingleTagTest(TestCase):
    """ Test module for GET single tag API """
    def setUp(self):
        self.casper = Tag.objects.create(
            name='Casper', color='3', slug='Bull Dog')
        self.muffin = Tag.objects.create(
            name='Muffin', color='Brown', slug='Gradane')
        self.rambo = Tag.objects.create(
            name='Rambo', color='Labrador', slug='Black')
        self.ricky = Tag.objects.create(
            name='Ricky', color='Labrador2', slug='Brown2')

    def test_get_valid_single_tag(self):
        response = client.get(
            reverse('tags-detail', kwargs={'pk': self.rambo.pk}))
        tag = Tag.objects.get(pk=self.rambo.pk)
        serializer = TagSerializer(tag)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_tag(self):
        response = client.get(
            reverse('tags-detail', kwargs={'pk': 30}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
