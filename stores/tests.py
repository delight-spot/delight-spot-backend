from rest_framework.test import APITestCase
from . import models
from users.models import User

class TestRooms(APITestCase):
    URL = "/api/v1/stores/"

    def setUp(self):
        user = User.objects.create(
            username="test",
        )
        user.set_password("1234")
        user.save()
        self.user = user

    def test_create_room(self):
        response = self.client.post(self.URL)
        self.assertEqual(response.status_code, 403)

        self.client.force_login(
            self.user,
        )
        response = self.client.post(self.URL)
        print(response.json())
