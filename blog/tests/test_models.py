from blog.models import Post, Category, Comment, Recipient
from .factories import PostFactory, CategoryFactory, CommentFactory, RecipientFactory, ReplyFactory
from django.test import TestCase
from datetime import datetime

class TestPostModel(TestCase):

    @classmethod
    def setUpTestData(cls): 
        cls.post = PostFactory()
        cls.post_with_categories = PostFactory.create(categories=[
                                                                 CategoryFactory(name="cat1"), 
                                                                 CategoryFactory(name="cat2"), 
                                                                 CategoryFactory(name="cat3"),])
        for _ in range(10):
            CommentFactory(name="commenter", 
                          email="commenter@email.com", 
                          comment="i am a comment", 
                          post=cls.post,)                                                        

    def test_post_str_method(self):
        post = self.post
        self.assertTrue(isinstance(post, Post)) 
        self.assertEqual(post.__str__(), post.slug)

    def test_post_get_absolute_url(self):
        post = self.post 
        first_post_url = f"/blog/{post.slug}" 
        self.assertEqual(first_post_url, post.get_absolute_url())  
   
    def test_adding_categories_to_post(self):  
        self.assertEqual(self.post_with_categories.categories.count(), 3) 

    def test_deletting_categories_from_post(self):
        self.post_with_categories.categories.filter(name__in=["cat1", "cat2"]).delete()  
        self.assertEqual(self.post_with_categories.categories.count(), 1)  

    def test_adding_comments_to_post(self): 
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 10)

    def test_deletting_comments_from_post(self):
        Comment.objects.filter(post=self.post)[0].delete() 
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 9)

    def test_just_created_posts_have_no_comments(self):
        just_created_post = PostFactory(title="just created post",
                                        body="this is the body of this post",
                                        pub_date= datetime.now(),
                                        slug="just-created-post",) 
        comments = Comment.objects.filter(post=just_created_post) 
        self.assertEqual(comments.count(), 0)                      


class TestCategoryModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = CategoryFactory()

    def test_category_str_method(self):
        category = self.category
        self.assertTrue(isinstance(category, Category))
        self.assertEqual(category.name, "a_category")
        self.assertEqual(category.__str__(), category.name)

    def test_category_get_absolute_url(self):
        category = self.category
        category_url = f"/blog/hashtag/{category.name}" 
        self.assertEqual(category_url, category.get_absolute_url())  

class TestCommentModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post_with_categories = PostFactory(title="post with category", 
                                               body = "this is a post with categories to test Comment model",
                                               pub_date= datetime.now(),
                                               slug = "post-with-category",)
        cls.comment = CommentFactory(name="commenter", 
                                    email="commenter@email.com", 
                                    comment="i am a comment", 
                                    post=cls.post_with_categories,)
        
        for i in range(5):
           ReplyFactory(name="Person", 
                        email="person@email.com", 
                        comment="i am a reply", 
                        parent_comment=cls.comment,)

      
    def test_comment_str_method(self):
        comment = self.comment
        self.assertTrue(isinstance(comment, Comment))
        self.assertEqual(comment.__str__(), comment.comment) 

    def test_comment_must_have_commenter_email_in__its_recipient_list_when_created(self): 
        # the commenter is the first recipient of their comment
        comment = self.comment
        self.assertEqual(comment.recipients.all().first().recipient_email, "commenter@email.com")    

    def test_adding_replies_to_comments(self): 
        comment = self.comment
        self.assertEqual(Comment.objects.filter(parent_comment=comment).count(), 5)  

    def test_when_new_person_reply_to_comment_new_email_is_added_to_comment_recipient_list(self):
        self.assertEqual(self.comment.recipients.all().count(), 2)
    
    def test_when_same_person_replies_to_same_comment_recipient_list_remains_the_same(self):
        ReplyFactory(name="Person",
                    email="person@email.com", 
                    comment="i am another reply", 
                    parent_comment=self.comment,)

        self.assertEqual(self.comment.recipients.all().count(), 2)

    def test_when_different_person_replies_to_same_comment_recipient_list_increases(self): 
        ReplyFactory(name="Different Person", 
                     email="diffirent-person@email.com",
                     comment="i a reply from a different person",
                     parent_comment=self.comment,)
        self.assertEqual(self.comment.recipients.all().count(), 3)
  
    def test_deletting_replies_from_comments(self):
        Comment.objects.filter(parent_comment=self.comment)[0].delete()
        self.assertEqual(Comment.objects.filter(parent_comment=self.comment).count(), 4)
    
           
class TestRecipientModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.recipient = RecipientFactory()   

    def test_comment_str_method(self):
        recipient = self.recipient
        self.assertTrue(isinstance(recipient, Recipient))
        self.assertEqual(recipient.recipient_email, "recipient@email.com")
        self.assertEqual(recipient.__str__(), recipient.recipient_email)
