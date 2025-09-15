from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.test import TestCase
from app.models import Actor

User = get_user_model()


class ActorAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin123"
        )
        self.regular_user = User.objects.create_user(
            username="user", email="user@example.com", password="user123"
        )
        self.actor = Actor.objects.create(name="Leonardo DiCaprio")

    def test_get_actor_list(self):
        url = reverse("actor-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Leonardo DiCaprio", str(response.data))

    def test_admin_can_create_actor(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("actor-list")
        response = self.client.post(url, {"name": "Tom Hanks"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Actor.objects.filter(name="Tom Hanks").exists())

    def test_user_cannot_create_actor(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("actor-list")
        response = self.client.post(url, {"name": "Tom Hanks"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_actor(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("actor-detail", args=[self.actor.id])
        response = self.client.put(url, {"name": "Leo"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.actor.refresh_from_db()
        self.assertEqual(self.actor.name, "Leo")

    def test_user_cannot_update_actor(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("actor-detail", args=[self.actor.id])
        response = self.client.put(url, {"name": "Leo"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_actor(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("actor-detail", args=[self.actor.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Actor.objects.filter(id=self.actor.id).exists())

    def test_user_cannot_delete_actor(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("actor-detail", args=[self.actor.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
