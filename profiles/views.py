# # Create your views here.
# from django.shortcuts import get_object_or_404
# from django.views.generic.list import ListView
# from django.views.generic.detail import DetailView
# from registration.models import Profile

# # Create your views here.

# class ProfileListView(ListView):
#     model = Profile
#     template_name = 'profiles/profile_list.html'
#     paginate_by = 3


# class ProfileDetailView(DetailView):
#     model = Profile
#     template_name = 'profiles/profile_detail.html'

#     def get_object(self):
#         return get_object_or_404(Profile, user__username=self.kwargs['username'])



# from django.contrib.auth.decorators import user_passes_test
# from django.views.generic.list import ListView
# from django.views.generic.detail import DetailView
# from django.shortcuts import get_object_or_404
# from registration.models import Profile


# @user_passes_test(lambda u: u.is_superuser)
# class ProfileListView(ListView):
#     model = Profile
#     template_name = 'profiles/profile_list.html'
#     paginate_by = 3


# @user_passes_test(lambda u: u.is_superuser)
# class ProfileDetailView(DetailView):
#     model = Profile
#     template_name = 'profiles/profile_detail.html'

#     def get_object(self):
#         return get_object_or_404(Profile, user__username=self.kwargs['username'])


from django.contrib.auth.decorators import user_passes_test
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from registration.models import Profile


class ProfileListView(ListView):
    model = Profile
    template_name = 'profiles/profile_list.html'
    paginate_by = 3

    @classmethod
    def as_view(cls, **kwargs):
        view = super().as_view(**kwargs)
        return user_passes_test(lambda u: u.is_superuser)(view)


class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'profiles/profile_detail.html'

    def get_object(self):
        return get_object_or_404(Profile, user__username=self.kwargs['username'])

    @classmethod
    def as_view(cls, **kwargs):
        view = super().as_view(**kwargs)
        return user_passes_test(lambda u: u.is_superuser)(view)
