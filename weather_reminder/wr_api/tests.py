from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.test import APIClient

from wr_api.models import User, Period


class APITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = str(AccessToken.for_user(self.user))
        self._client = APIClient()

    def test_secure_endpoint(self):
        self._client.credentials(HTTP_AUTHORIZATION=f'Bearer INVALID_TOKEN')
        response = self._client.get(reverse('subscriptions'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  # INVALID TOKEN

        self._client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self._client.get(reverse('subscriptions'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)            # CORRECT TOKEN

    def test_create_sub_non_exist_period(self):
        self._client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        response = self._client.post(reverse('subscriptions'), data={
            "location": "Poltava",
            "period": 1
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)   # non-existent period

    def test_create_sub_unsupported_location(self):
        self._client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        Period.objects.create(interval=1, hours="0,12")
        response = self._client.post(reverse('create_subscription'), data={         # Unsupported location
            "location": "UNSOPPORTED_CITY",
            "period": 1
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sub_correct_location(self):
        self._client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        Period.objects.create(interval=1, hours="0,12")
        response = self._client.post(reverse('create_subscription'), data={         # Correct location
            "location": "Lviv",
            "period": 1
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_subscription(self):
        self._client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        response = self._client.get(reverse('subscriptions'), {"pk": 1})            # subscription details
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_subscription(self):
        self._client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        Period.objects.create(interval=1, hours="0,12")

        response = self._client.post(reverse('create_subscription'), data={         # Correct location
            "location": "Lviv",
            "period": 1
        })
        sub_id = response.json().get('subscription').get('id')

        url = reverse('update_subscription', kwargs={"pk": sub_id})                # update subscription
        response = self._client.patch(url, data={"location": "Poltava"})
        self.assertEqual(response.json().get('subscription').get('info').get('location'),
                         "Poltava")

    def test_delete_subscription(self):
        self._client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        Period.objects.create(interval=1, hours="0,12")

        response = self._client.post(reverse('create_subscription'), data={         # Correct location
            "location": "Lviv",
            "period": 1
        })
        sub_id = response.json().get('subscription').get('id')

        url = reverse('delete_subscription', kwargs={"pk": sub_id})                # delete subscription
        response = self._client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_user(self):

        url = reverse('register')

        response = self._client.post(url, data={                                      # create user
            'username': 'testusername',
            'password': 'testpassword',
            'email': 'test@e.mail'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get('user_info'), "testusername, test@e.mail")

    def test_get_JWT(self):
        url = reverse('register')

        self._client.post(url, data={                                      # create user
            'username': 'testusername',
            'password': 'testpassword',
            'email': 'test@e.mail'
        })

        url = reverse('token_obtain_pair')
        response = self._client.post(url, data={                                     # get JWT
            'username': 'testusername',
            'password': 'testpassword',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_via_JWT(self):
        url = reverse('register')

        self._client.post(url, data={                                      # create user
            'username': 'testusername',
            'password': 'testpassword',
            'email': 'test@e.mail'
        })
        url = reverse('token_obtain_pair')
        response = self._client.post(url, data={                                     # get JWT
            'username': 'testusername',
            'password': 'testpassword',
        })

        access_token = response.json().get('access')
        self._client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self._client.get(reverse('subscriptions'))                       # check auth via JWT
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_JWT(self):
        url = reverse('register')

        self._client.post(url, data={                                      # create user
            'username': 'testusername',
            'password': 'testpassword',
            'email': 'test@e.mail'
        })
        url = reverse('token_obtain_pair')
        response = self._client.post(url, data={                                     # get JWT
            'username': 'testusername',
            'password': 'testpassword',
        })

        refresh_token = str(response.json().get('refresh'))

        url = reverse('token_refresh')
        response = self._client.post(url, data={                                     # refresh token
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
