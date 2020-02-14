from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name="index_view"),
    # a link to all the posts that have <category> in their set of categories 
    path('hashtag/<category>', views.CategoryIndexView.as_view(), name="category_index_view"),
    # a link to a specific post whose slug=<slug> 
    path('<slug>', views.PostDetailView.as_view(), name='post_detail_view'),  
    path('unsubscribe/all-posts-on-voila', views.unsubscribe_from_all_posts, name="unsubscribe_from_all_posts_view"),
    # a link to unsubscribe from the comment whose id=<comment_id>
    # so that the commenter no longer recieve email notifications
    # when someone replies to their comment
    path('unsubscribe/<comment_id>', views.unsubscribe_from_comment, name="unsubscribe_from_post_view"),
]