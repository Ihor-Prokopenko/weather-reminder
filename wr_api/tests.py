from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.test import APIClient

from wr_api.models import User, Period


class SecureAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = str(AccessToken.for_user(self.user))

    def test_secure_endpoint(self):
        client = APIClient()

        client.credentials(HTTP_AUTHORIZATION=f'Bearer INVALID_TOKEN')
        response = client.get(reverse('subscriptions'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  # INVALID TOKEN

        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = client.get(reverse('subscriptions'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)            # CORRECT TOKEN

    def test_subscriptions(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        response = client.post(reverse('subscriptions'), data={
            "location": "Poltava",
            "period": 1
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)   # non-existent period

        Period.objects.create(interval=1, hours="0,12")

        response = client.post(reverse('create_subscription'), data={         # Unsupported location
            "location": "UNSOPPORTED_CITY",
            "period": 1
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = client.post(reverse('create_subscription'), data={         # Correct location
            "location": "Lviv",
            "period": 1
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.get(reverse('subscriptions'), {"pk": 1})            # subscription details
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('update_subscription', kwargs={"pk": 1})                # update subscription
        response = client.patch(url, data={"location": "Poltava"})
        self.assertEqual(response.json().get('subscription').get('info').get('location'),
                         "Poltava")

        url = reverse('delete_subscription', kwargs={"pk": 1})                # delete subscription
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_auth(self):
        client = APIClient()

        url = reverse('register')

        response = client.post(url, data={                                      # create user
            'username': 'testusername',
            'password': 'testpassword',
            'email': 'test@e.mail'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get('user_info'), "testusername, test@e.mail")

        url = reverse('token_obtain_pair')
        response = client.post(url, data={                                     # get JWT
            'username': 'testusername',
            'password': 'testpassword',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        access_token = response.json().get('access')
        refresh_token = response.json().get('refresh')

        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = client.get(reverse('subscriptions'))                       # check auth via JWT
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('token_refresh')
        response = client.post(url, data={                                     # refresh token
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
