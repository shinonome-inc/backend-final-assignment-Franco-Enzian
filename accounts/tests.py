from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import FriendShip
from tweets.models import Tweet

User = get_user_model()


class TestSignupView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, valid_data)
        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        invalid_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])

    def test_failure_post_with_empty_username(self):
        invalid_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])

    def test_failure_post_with_empty_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["email"])

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["password1"])

    def test_failure_post_with_duplicated_user(self):
        User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertIn("同じユーザー名が既に登録済みです。", form.errors["username"])

    def test_failure_post_with_invalid_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("有効なメールアドレスを入力してください。", form.errors["email"])

    def test_failure_post_with_too_short_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "arigato",
            "password2": "arigato",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは短すぎます。最低 8 文字以上必要です。", form.errors["password2"])

    def test_failure_post_with_password_similar_to_username(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testusers",
            "password2": "testusers",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは ユーザー名 と似すぎています。", form.errors["password2"])

    def test_failure_post_with_only_numbers_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "123456789",
            "password2": "123456789",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは数字しか使われていません。", form.errors["password2"])

    def test_failure_post_with_mismatch_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpasswords",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("確認用パスワードが一致しません。", form.errors["password2"])


class TestLoginView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        self.url = reverse(settings.LOGIN_URL)

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        response = self.client.post(self.url, {"username": "testuser", "password": "testpassword"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        invalid_data = {
            "username": "not_exist",
            "password": "testpass",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertIn("正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。", form.errors["__all__"])

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "password": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertIn("このフィールドは必須です。", form.errors["password"])


class TestLogoutView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:logout")
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL), status_code=302, target_status_code=200)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        self.tweet = Tweet.objects.create(user=self.user, content="TestContent")
        self.other_tweet = Tweet.objects.create(user=self.user, content="TestContent2")
        self.url = reverse("accounts:user_profile", kwargs={"username": self.user.username})

    def test_success_get(self):
        response = self.client.get(self.url)
        context_tweets = response.context["tweets"]
        user_tweets_in_db = Tweet.objects.filter(user=self.user).order_by("-created_at")
        self.assertQuerysetEqual(context_tweets, user_tweets_in_db, ordered=False)


class TestUserProfileEditView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpassword")
        other_user = User.objects.create_user(username="other_user", password="testpassword")
        FriendShip.objects.create(following=self.user, followed=other_user)
        FriendShip.objects.create(following=other_user, followed=self.user)
        self.url = reverse("accounts:user_profile", kwargs={"username": self.user.username})

    def test_success_get(self):
        response = self.client.get(reverse("accounts:user_profile", kwargs={"username": self.user.username}))
        context_followers_count = response.context["followers_count"]
        context_following_count = response.context["following_count"]

        followers_count = FriendShip.objects.filter(followed=self.user).count()
        following_count = FriendShip.objects.filter(following=self.user).count()

        self.assertEqual(context_followers_count, followers_count)
        self.assertEqual(context_following_count, following_count)


class TestFollowView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.other_user = User.objects.create_user(username="other_user", password="testpassword")
        self.client.login(username="tester", password="testpassword")

    def test_success_post(self):
        self.url = reverse("accounts:follow", kwargs={"username": self.other_user.username})
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(FriendShip.objects.filter(following=self.user).exists())

    def test_failure_post_with_not_exist_user(self):
        self.url = reverse("accounts:follow", kwargs={"username": "non_exist_user"})
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(FriendShip.objects.filter(following=self.user).exists())

    def test_failure_post_with_self(self):
        self.url = reverse("accounts:follow", kwargs={"username": self.user.username})
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(FriendShip.objects.filter(following=self.user).exists())


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.other_user = User.objects.create_user(username="other_user", password="testpassword")
        FriendShip.objects.create(following=self.user, followed=self.other_user)
        self.client.login(username="tester", password="testpassword")

    def test_success_post(self):
        self.url = reverse("accounts:unfollow", kwargs={"username": self.other_user.username})
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(FriendShip.objects.filter(following=self.user).exists())

    def test_failure_post_with_not_exist_user(self):
        self.url = reverse("accounts:unfollow", kwargs={"username": "not_exist_user"})
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(FriendShip.objects.filter(following=self.user).exists())

    def test_failure_post_with_self(self):
        self.url = reverse("accounts:unfollow", kwargs={"username": self.user.username})
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(FriendShip.objects.filter(following=self.user).exists())


class TestFollowingListView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.other_user = User.objects.create_user(username="other_user", password="testpassword")
        self.friendship = FriendShip.objects.create(following=self.user, followed=self.other_user)
        self.url = reverse("accounts:following_list", kwargs={"username": self.user.username})

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class TestFollowerListView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.other_user = User.objects.create_user(username="other_user", password="testpassword")
        self.friendship = FriendShip.objects.create(following=self.other_user, followed=self.user)
        self.url = reverse("accounts:follower_list", kwargs={"username": self.user.username})

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
