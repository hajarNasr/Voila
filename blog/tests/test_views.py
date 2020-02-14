from django.test import TestCase
from django.urls import reverse
from blog.models import Post, Category, Comment, Recipient
from blog.forms import CommentForm, ReplyForm, UnsubscribeForm
from django.core import mail
from voila.settings import MY_EMAIL as my_email

class TestIndexView(TestCase):
    @classmethod
    def setUpTestData(cls):
        #create 9 post objects for tests
        for post_id in range (1, 10):
            Post.objects.create(title=f"Post No. {post_id}", 
                                body=f"I am the body of post no.{post_id}",)
    
    def test_index_view_url_path(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

    def test_correct_template_is_used_when_rendering_index_view(self):
        response = self.client.get(reverse('blog:index_view'))
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'blog/blog-index.html')

    def test_post_pagination_is_five(self):
        response = self.client.get(reverse('blog:index_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['posts']), 5)

    def test_remained_posts_to_be_viewed_in_the_second_page_is_four(self):
        # the posts in the second page must be four because there are 9 posts and index_view is paginate_by by 5
        response = self.client.get(reverse('blog:index_view')+"?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['posts']), 4)    

class TestCategoryIndexView(TestCase):
    @classmethod
    def setUpTestData(cls):
        # create 9 category objects with the name first_category and assign them to nine posts
        for post_id in range(1, 10):
            cls.category = Category.objects.create(name="first_category")
            Post.objects.create(title=f"Post No. {post_id}", 
                                body=f"I am the body of post no.{post_id}").categories.add(cls.category)

    def test_category_index_view_url_path(self):
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)
    
    def test_correct_template_is_used_when_rendering_category_index_view(self):
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/category-index-view.html')

    def test_posts_with_specific_category_pagination_is_five(self): 
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['posts']), 5)

    def test_remained_posts_to_be_viewed_in_the_second_page_is_four(self):
        # the posts in the second page must be four because there are 9 posts with 9 categories with the name first_category
        # and category_index_view is paginate_by by 5
        response = self.client.get(self.category.get_absolute_url()+"?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['posts']), 4)    

class TestPostDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post = Post.objects.create(title="New Post for Tests", 
                                        body="I am the body of a post that's created only for tests.",
                                        slug="new-post-for-tests",)
        cls.category = Category.objects.create(name="category_for_tests")  
        cls.post.categories.add(cls.category) 

        cls.comment = Comment.objects.create(name="Person", 
                                             email="person@email.com", 
                                             comment="I am a comment for tests",
                                             post=cls.post,)
        cls.recipient = Recipient.objects.create(recipient_email=cls.comment.email)
        cls.comment.recipients.add(cls.recipient)                       

    def test_post_detail_view_url_path(self):
        response = self.client.get('/blog/new-post-for-tests')
        self.assertEqual(response.status_code, 200)                                
    
    def test_correct_template_is_used_when_rendering_post_detail_view(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, "blog/post-detail.html")

    def test_post_has_the_right_count_of_categories(self):
        post = self.post  
        post.categories.add(Category.objects.create(name="second_category"))
        categories = post.categories.all()
        response = self.client.get(post.get_absolute_url())

        self.assertEqual(response.status_code, 200) 
        self.assertEqual(categories.count(), 2)
        self.assertEqual(categories[0].name, "category_for_tests")
        self.assertEqual(categories[1].name, "second_category")
    
    def test_post_has_the_right_count_of_comments(self):
        post = self.post
        response = self.client.get(post.get_absolute_url())
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.context['comments'][0].comment, self.comment.comment)
        self.assertEqual(response.context['comments_count'], 1)

    def test_detail_page_of_post_with_comments_has_comment_and_reply_forms(self): 
        post = self.post
        response = self.client.get(post.get_absolute_url())
        self.assertEqual(response.status_code, 200) 
        self.assertTrue('comment_form' in response.context)
        self.assertTrue('reply_form' in response.context) 
        self.assertTrue(isinstance(response.context['comment_form'], CommentForm))  
        self.assertTrue(isinstance(response.context['reply_form'], ReplyForm))

    def test_detail_page_of_post_with_no_comments_has_only_comment_form(self): 
        post = Post.objects.create(title="Post Without Comments",
                                   body="I am a post with no comments yet, so I should only have one form for adding comments.",
                                   slug="post-without-comments",)

        response = self.client.get(post.get_absolute_url())
        self.assertEqual(response.status_code, 200)  
        self.assertTrue('comment_form' in response.context)
        self.assertFalse('reply_form' in response.context)      

    def test_when_adding_new_comments_to_post_post_detail_page_renders_with_the_new_comments(self):
        post = self.post
        comment_form = CommentForm({'name': "Another Person", 'email': "another-person@email.com", 'comment': "I am just a comment",})
        self.assertTrue(comment_form.is_valid())

        new_comment = Comment.objects.create(name=comment_form.cleaned_data["name"],
                                             email=comment_form.cleaned_data["email"],
                                             comment=comment_form.cleaned_data["comment"],
                                             post = post,)
        
        response = self.client.get(post.get_absolute_url())
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.context['comments'][0].comment, self.comment.comment)
        self.assertEqual(response.context['comments'][1].comment, new_comment.comment)
        self.assertEqual(response.context['comments_count'], 2)
    
    def test_post_method_in_post_detail_view_when_adding_new_comments(self):
        post = self.post
        email = "someemail@email.com"
        self.assertEqual(Comment.objects.filter(post=post).count(), 1)
        self.assertTrue(email not in [recipient.recipient_email for recipient in Recipient.objects.all()])

        response = self.client.post(post.get_absolute_url(), {"name":"Someone", 
                                                              "email":email, 
                                                              "comment":"this is a new comment",})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post-detail.html")
        # the comment has been added
        self.assertEqual(Comment.objects.filter(post=post).count(), 2)
        # and the commenter's email has been added to the recipients
        self.assertTrue(email in [recipient.recipient_email for recipient in Recipient.objects.all()])

        response = self.client.post(post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # the comment gets rendered with post
        self.assertEqual(response.context['comments_count'], 2)
        self.assertEqual(response.context['comments'][1].comment, "this is a new comment")
    
    def test_post_method_in_post_detail_view_when_adding_replies_to_comments(self):
        post = self.post
        comment = self.comment
        email = "another-person@email.com"
        self.assertEqual(comment.replies.all().count(), 0) 
        self.assertTrue(email not in [recipient.recipient_email for recipient in comment.recipients.all()])

        response = self.client.post(post.get_absolute_url(), {"name":"Another Person", 
                                                              "email":email,
                                                              "comment":"I am a reply.",
                                                              "parent_comment_id":comment.id,})
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post-detail.html")
        # a new reply has been added to comment
        self.assertEqual(comment.replies.all().count(), 1)
        # and a new email has been added to the recipients list
        self.assertTrue(email in [recipient.recipient_email for recipient in comment.recipients.all()])

    def test_sendding_email_to_my_email_when_someone_comments_on_post(self):
        post = self.post
        response = self.client.post(post.get_absolute_url(), {"name":"Person", 
                                                              "email":"commenter@email.com",
                                                              "comment":"I am a comment.",})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "A new comment from Voila")
        self.assertEqual(mail.outbox[0].body, f"Someone commented on {post.get_absolute_url()}")
        self.assertEqual(mail.outbox[0].to[0], my_email)

        response = self.client.post(post.get_absolute_url(), {"name":"Another Person", 
                                                              "email":"anotherp@email.come",
                                                              "comment":"I am another comment.",})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 2)

    def test_notify_recipients_of_new_reply_is_added(self):
        comment = self.comment
        post = self.post
        response = self.client.post(post.get_absolute_url(), {"name":"Person", 
                                                              "email":"newemail@email.com",
                                                              "comment":"I am a reply.", 
                                                              "parent_comment_id": comment.id,})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.replies.all().count(), 1)
        self.assertEqual(comment.recipients.all().count(), 2)
        # an email is sent to the comment's owner to notify them of the new reply
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "A new reply from Voila")
        self.assertEqual(mail.outbox[0].to[0], comment.email)
        self.assertTemplateUsed(response, 'blog/email-template.html')
   

class TestUnsubscribeViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post = Post.objects.create(title="A Post", 
                                      body="I am a post",)
        cls.comment = Comment.objects.create(name="Someone", 
                                            email="someonesomeone@email.com", 
                                            comment="I am a comment", 
                                            post=cls.post,)
        cls.recipient= Recipient(recipient_email="someonesomeone@email.com")
        cls.recipient.save()
        cls.comment.recipients.add(cls.recipient)
  
    def test_rerender_when_blank_email(self):  
        self.assertEqual(self.comment.recipients.all().count(), 1) 
        response = self.client.post(reverse('blog:unsubscribe_from_post_view', 
                                    kwargs={'comment_id': self.comment.id}),
                                    {"email":""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/unsubsribe-email.html")  
         # the recipients count remains the same
        self.assertEqual(self.comment.recipients.all().count(), 1)
 
    def test_rerender_with_error_message_when_wrong_email(self):
        self.assertEqual(self.comment.recipients.all().count(), 1) 
        response = self.client.post(reverse('blog:unsubscribe_from_post_view', 
                                    kwargs={'comment_id': self.comment.id}),
                                    {"email":"wrong-email@email.com"})
        messages = list(response.context["messages"])                              
        self.assertEqual(str(messages[0]), "The email you entered is not subscribed to any post.")
        self.assertTemplateUsed(response, "blog/unsubsribe-email.html") 
        # the recipients count remains the same
        self.assertEqual(self.comment.recipients.all().count(), 1) 

    def test_unsubscribe_when_correct_email(self):
        # delete the commenter from the recipients list so they now longer get notified when someone replies to their comment
        comment = self.comment
        self.assertEqual(comment.recipients.all().count(), 1) 
        response = self.client.post(reverse('blog:unsubscribe_from_post_view',
                                   kwargs={'comment_id': comment.id}), 
                                   {"email":comment.email})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/successfully-unsubscribed.html")
         # the recipients count decreases
        self.assertEqual(comment.recipients.all().count(), 0) 
    
    def test_rerender_unsubscribe_from_all_posts_view_with_error_message_when_wrong_email(self):
        response = self.client.post(reverse('blog:unsubscribe_from_all_posts_view'),
                                    {'email':"wrong-email@email.com"})
        messages = list(response.context["messages"])                              
        self.assertEqual(str(messages[0]), "The email you entered is not subscribed to any post.")
        self.assertTemplateUsed(response, "blog/unsubsribe-email.html")                             

    def test_unsubscribe_from_all_posts_when_correct_email(self):
        comment = self.comment
        new_recipient = Recipient.objects.create(recipient_email="new-recipien@email.com")
        comment.recipients.add(new_recipient)
        new_comment = Comment.objects.create(name="new comment", 
                                             email="newcomment@eamil.com", 
                                             comment="I am a new comment",)  
        new_comment.recipients.add(new_recipient)

        response = self.client.post(reverse('blog:unsubscribe_from_all_posts_view'),
                                    {'email':new_recipient.recipient_email})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/successfully-unsubscribed.html")  
        # there's no longer a recipient with the given email
        self.assertEqual(Recipient.objects.filter(recipient_email=new_recipient.recipient_email).count(), 0)                          
        






        
        


       
