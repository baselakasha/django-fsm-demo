from django.urls import path, include

from .api_router import router
from .views import DissaprovePost, EditPost, IndexView, AboutView, ListOwnPosts, LoginPageView, \
     SignupView, LogoutView, AddPost, SubmitPost, UnpublishPost, ViewPost, AdminViewPostsThatNeedApproval, ApprovePost

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('about/', AboutView.as_view(), name="about"),
    path('login/', LoginPageView.as_view(), name="loginPage"),
    path('signup/', SignupView.as_view(), name="signup"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('api/', include(router.urls)),
    
    path('post/add/', AddPost.as_view(), name="add_post"),
    path("post/<int:pk>/", ViewPost.as_view(), name="view_post"),
    path("post/submit/<int:pk>/", SubmitPost.as_view(), name="submit_post"),
    path("post/edit/<int:pk>/", EditPost.as_view(), name="edit_post"),
    path('post/list/mine', ListOwnPosts.as_view(), name="list_own_posts"),
    path("post/list/needs-approval/", AdminViewPostsThatNeedApproval.as_view(), name="need_approval_posts"),
    
    path("post/approve/<int:pk>/", ApprovePost.as_view(), name="approve_post"),
    path("post/disapprove/<int:pk>/", DissaprovePost.as_view(), name="disapprove_post"),
    path("post/unpublish/<int:pk>/", UnpublishPost.as_view(), name="unpublish_post"),
]