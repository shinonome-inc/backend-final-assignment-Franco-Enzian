# from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView

from tweets.models import Tweet


class HomeView(LoginRequiredMixin, ListView):
    model = Tweet
    context_object_name = "tweets"
    template_name = "tweets/home.html"
    queryset = Tweet.objects.select_related("user")


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
