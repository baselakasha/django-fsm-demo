from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, ListView
from django.views.generic.edit import UpdateView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin

from django_fsm import has_transition_perm

from .forms import CreateUserForm
from .models  import BlogPost


class IndexView(TemplateView):
    template_name = 'app/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = BlogPost.objects.filter(state="published")
        return context


class AboutView(TemplateView):
    template_name = 'app/about.html'


class SignupView(TemplateView):
    template_name = 'app/signup.html'
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, "app/index.html")
        form = CreateUserForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, "app/thanks.html", {'form': form})

        return render(request, self.template_name, {'form': form})


class LoginPageView(TemplateView):
    template_name = 'app/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')

        return render(
            request,
            self.template_name,
            {
                'error_message':
                'Email or password is incorrect'
            }
        )


class LogoutView(TemplateView):
    template_name = 'app/logout.html'

    def get(self, request,  *args, **kwargs):
        logout(request)
        return redirect('index')


class AddPost(LoginRequiredMixin, CreateView):
    template_name = 'app/post/add-post.html'
    fields = ['title', 'content']

    success_url = '/'
    model = BlogPost
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class SubmitPost(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        post = BlogPost.objects.get(pk=pk)

        if not has_transition_perm(post.submit, request.user):
            raise PermissionDenied

        post.submit()
        post.save()
        return redirect('index')


class ViewPost(DetailView):
    template_name = 'app/post/view-post.html'
    model = BlogPost


class EditPost(LoginRequiredMixin, UpdateView):
    template_name = 'app/post/edit-post.html'
    fields = ['title', 'content']
    model = BlogPost
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        if not has_transition_perm(form.instance.edit, self.request.user):
            raise PermissionDenied

        form.instance.edit()
        
        return super().form_valid(form)


class ListOwnPosts(LoginRequiredMixin, ListView):
    template_name = 'app/post/list-post.html'
    model = BlogPost
    def get_queryset(self):
        return BlogPost.objects.filter(author=self.request.user)


class AdminViewPostsThatNeedApproval(LoginRequiredMixin, ListView):
    template_name = 'app/post/list-needs-approval.html'
    model = BlogPost
    
    def get_queryset(self):
        return BlogPost.objects.filter(state='waiting approval')
    

class ApprovePost(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        post = BlogPost.objects.get(pk=pk)

        if not has_transition_perm(post.approve, request.user):
            raise PermissionDenied
    
        post.approve()
        post.save()
        return redirect('index')


class DissaprovePost(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        post = BlogPost.objects.get(pk=pk)

        if not has_transition_perm(post.disapprove, request.user):
            raise PermissionDenied

        post.dissaprove()
        post.save()
        return redirect('index')
    

class UnpublishPost(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        post = BlogPost.objects.get(pk=pk)

        if not has_transition_perm(post.unpublish, request.user):
            raise PermissionDenied

        post.unpublish()
        post.save()

        return redirect('index')

