from django.contrib.auth import get_user_model

# from django.contrib.auth import SESSION_KEY,
from django.test import TestCase
from django.urls import reverse

from tweets.models import Like, Tweet

User = get_user_model()


class TestHomeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.client.login(username="tester", password="testpassword")
        self.tweet = Tweet.objects.create(user=self.user, content="TestContent")
        other_user = User.objects.create_user(username="other_user", password="testpassword")
        Tweet.objects.create(user=other_user, content="OtherTestContent")
        self.url = reverse("tweets:home")

    def test_success_get(self):
        response = self.client.get(self.url)
        context_tweets = response.context["tweets"]
        db_tweets = Tweet.objects.all().order_by("id")
        self.assertEqual(list(context_tweets), list(db_tweets))


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.client.login(username="tester", password="testpassword")
        self.url = reverse("tweets:create")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        post_data = {"content": "This is a test tweet!"}
        response = self.client.post(self.url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("tweets:home"))
        self.assertTrue(Tweet.objects.filter(id=1).exists())
        self.assertEqual(Tweet.objects.get(id=1).content, post_data["content"])

    def test_failure_post_with_empty_content(self):
        not_available_data = {"content": ""}
        response = self.client.post(self.url, not_available_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("このフィールドは必須です。", form.errors["content"])
        self.assertFalse(Tweet.objects.filter(id=1).exists())

    def test_failure_post_with_too_long_content(self):
        too_long_content = "a" * (Tweet._meta.get_field("content").max_length + 1)
        max_length = Tweet._meta.get_field("content").max_length
        response = self.client.post(self.url, {"content": too_long_content})
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue("このフィールドの文字数は {0} 文字以下にしてください。".format(max_length), form.errors["content"])
        self.assertFalse(Tweet.objects.filter(id=1).exists())


class TestTweetDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(user=self.user, content="test_content")
        self.url = reverse("tweets:detail", args=[str(self.tweet.id)])

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tweet"], self.tweet)


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(user=self.user, content="test_content")
        self.url = reverse("tweets:delete", args=(self.tweet.id,))

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("tweets:home"))
        self.assertFalse(Tweet.objects.filter(id=self.tweet.id).exists())

    def test_failure_post_with_not_exist_tweet(self):
        not_exist_tweet_id = self.tweet.id + 1
        url = reverse("tweets:delete", args=(not_exist_tweet_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Tweet.objects.filter(id=self.tweet.id).exists())

    def test_failure_post_with_incorrect_user(self):
        another_user = User.objects.create_user(
            username="another_testuser", password="testpassword", email="another@another.com"
        )
        another_user_tweet = Tweet.objects.create(user=another_user, content="test_another_content")
        url = reverse("tweets:delete", args=(another_user_tweet.id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Tweet.objects.filter(id=self.tweet.id).exists())


class TestLikeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def test_success_post(self):
        another_user = User.objects.create_user(
            username="another_testuser", password="testpassword", email="another@another.com"
        )
        another_user_tweet = Tweet.objects.create(user=another_user, content="test_another_content")
        url = reverse("tweets:like", args=(another_user_tweet.id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.filter(user=self.user).exists())

    def test_failure_post_with_not_exist_tweet(self):
        another_user = User.objects.create_user(
            username="another_testuser", password="testpassword", email="another@another.com"
        )
        another_user_tweet = Tweet.objects.create(user=another_user, content="test_another_content")
        not_exist_tweet_id = another_user_tweet.id + 1
        url = reverse("tweets:like", args=(not_exist_tweet_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Like.objects.filter(user=self.user).exists())

    def test_failure_post_with_liked_tweet(self):
        another_user = User.objects.create_user(
            username="another_testuser", password="testpassword", email="another@another.com"
        )
        another_user_tweet = Tweet.objects.create(user=another_user, content="test_another_content")
        Like.objects.create(user=self.user, tweet=another_user_tweet)
        url = reverse("tweets:like", args=(another_user_tweet.id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.filter(user=self.user).exists())


class TestUnLikeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def test_success_post(self):
        another_user = User.objects.create_user(
            username="another_testuser", password="testpassword", email="another@another.com"
        )
        another_user_tweet = Tweet.objects.create(user=another_user, content="test_another_content")
        Like.objects.create(user=self.user, tweet=another_user_tweet)
        url = reverse("tweets:unlike", args=(another_user_tweet.id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Like.objects.filter(user=self.user).exists())

    def test_failure_post_with_not_exist_tweet(self):
        another_user = User.objects.create_user(
            username="another_testuser", password="testpassword", email="another@another.com"
        )
        another_user_tweet = Tweet.objects.create(user=another_user, content="test_another_content")
        Like.objects.create(user=self.user, tweet=another_user_tweet)
        not_exist_tweet_id = another_user_tweet.id + 1
        url = reverse("tweets:unlike", args=(not_exist_tweet_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Like.objects.filter(user=self.user).exists())

    def test_failure_post_with_unliked_tweet(self):
        another_user = User.objects.create_user(
            username="another_testuser", password="testpassword", email="another@another.com"
        )
        another_user_tweet = Tweet.objects.create(user=another_user, content="test_another_content")
        Like.objects.create(user=self.user, tweet=another_user_tweet)
        UnLike = Like.objects.get(id=1)
        UnLike.delete()

        url = reverse("tweets:unlike", args=(another_user_tweet.id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
