# from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, View
from django.views.generic.edit import CreateView

from tweets.models import Like, Tweet


class HomeView(LoginRequiredMixin, ListView):
    model = Tweet
    context_object_name = "tweets"
    template_name = "tweets/home.html"
    queryset = Tweet.objects.select_related("user").prefetch_related("likes").all().order_by("-created_at")


class TweetCreateView(CreateView):
    model = Tweet
    fields = ["content"]
    template_name = "tweets/create.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDetailView(DetailView):
    model = Tweet
    template_name = "tweets/detail.html"


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tweet
    template_name = "tweets/delete.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def test_func(self):
        tweet = self.get_object()
        return tweet.user == self.request.user


class LikeView(LoginRequiredMixin, View):
    model = Like

    def post(self, request, *args, **kwargs):
        target_tweet_id = self.kwargs.get("pk")

        try:
            target_tweet = Tweet.objects.get(pk=target_tweet_id)
        except Tweet.DoesNotExist:
            raise Http404("Tweet not found")

        liked_by = request.user
        Like.objects.get_or_create(tweet=target_tweet, user=liked_by)
        context = {"likes_count": target_tweet.likes.count()}
        return JsonResponse(context)


class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        target_tweet_id = self.kwargs.get("pk")

        try:
            target_tweet = Tweet.objects.get(pk=target_tweet_id)
        except Tweet.DoesNotExist:
            raise Http404("Tweet not found")

        liked_by = request.user
        Like.objects.filter(tweet=target_tweet, user=liked_by).delete()
        context = {"likes_count": target_tweet.likes.count()}
        return JsonResponse(context)
