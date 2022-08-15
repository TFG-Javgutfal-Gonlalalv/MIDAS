from django.test import TestCase
from django.urls import reverse
from rest_framework import status


# Create your tests here.
class ApiTestCase(TestCase):

    def test_get_runs(self):
        #response = self.client.get(reverse('runs'))
        print("response")
        #self.assertEqual(response.status_code, status.HTTP_200_OK)
