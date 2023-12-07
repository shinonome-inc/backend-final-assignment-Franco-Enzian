# from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, View

from accounts.models import FriendShip, User
from tweets.models import Tweet

from .forms import SignupForm


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class UserProfileView(TemplateView):
    model = Tweet
    template_name = "accounts/user_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs["username"]
        profile_user = get_object_or_404(User, username=username)
        followers_count = FriendShip.objects.filter(followed=profile_user).count()
        following_count = FriendShip.objects.filter(following=profile_user).count()
        context["profile_user"] = profile_user
        context["tweets"] = Tweet.objects.filter(user=profile_user).order_by("-created_at")
        context["followers_count"] = followers_count
        context["following_count"] = following_count
        return context


class FollowView(LoginRequiredMixin, View):
    model = FriendShip

    def post(self, request, username):
        followed_user = get_object_or_404(User, username=username)
        following_user = self.request.user

        # 自分自身をフォローしようとした場合
        if followed_user == following_user:
            return HttpResponseBadRequest("自分自身をフォローすることはできません。")
        # 既にフォローしている場合
        if FriendShip.objects.filter(following=following_user, followed=followed_user).exists():
            return HttpResponseBadRequest("既にフォローしています。")

        # フォロー関係を作成
        FriendShip.objects.get_or_create(following=following_user, followed=followed_user)
        return redirect(settings.LOGIN_REDIRECT_URL)


class UnFollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        username_to_unfollow = self.kwargs.get("username")
        followed_user = get_object_or_404(User, username=username_to_unfollow)
        following_user = self.request.user

        try:
            friendship = FriendShip.objects.get(following=following_user, followed=followed_user)
            friendship.delete()
            return redirect(settings.LOGIN_REDIRECT_URL)
        except FriendShip.DoesNotExist:
            return HttpResponseBadRequest("このユーザーをフォローしていません。")


class FollowingListView(ListView):
    model = FriendShip
    template_name = "accounts/following_list.html"

    def get_queryset(self):
        username = self.kwargs["username"]
        user = User.objects.get(username=username)
        return FriendShip.objects.filter(following=user)


class FollowerListView(ListView):
    model = FriendShip
    template_name = "accounts/follower_list.html"

    def get_queryset(self):
        username = self.kwargs["username"]
        user = User.objects.get(username=username)
        return FriendShip.objects.filter(followed=user)
