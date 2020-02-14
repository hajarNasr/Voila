from django.test import TestCase
from blog.forms import CommentForm, ReplyForm, UnsubscribeForm 
from .factories import CommentFactory, ReplyFactory

class TestCommentForm(TestCase):
    def test_comment_form_is_valid_when_valid_data(self):
        comment_form = CommentForm({
               'name': "Person",
               'email': "person@email.com",
               'comment': "I am a comment",
        })
        self.assertTrue(comment_form.is_valid())
        comment = comment_form.save()
        self.assertEqual(comment.name,"Person")
        self.assertEqual(comment.email, "person@email.com")
        self.assertEqual(comment.comment, "I am a comment")

    def test_comment_form_is_not_valid_when_blank_data(self):
        comment_form = CommentForm({})
        self.assertFalse(comment_form.is_valid())  
        self.assertEqual(comment_form.errors, {
            'name': ['This field is required.'],
            'email': ['This field is required.'],
            'comment': ['This field is required.']
        })  
        comment_form = CommentForm({"name":"Another Person",})  
        self.assertFalse(comment_form.is_valid())   
        self.assertEqual(comment_form.errors, {
            'email': ['This field is required.'],
            'comment': ['This field is required.']
        })
        comment_form = CommentForm({"name":"Another Person", "email":"anotherperson@email.com",})
        self.assertFalse(comment_form.is_valid())
        self.assertEqual(comment_form.errors, {
            'comment': ['This field is required.']
        })

class TestReplyForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.comment = CommentFactory()
    def test_reply_form_is_valid_when_valid_data(self):
        comment = self.comment
        reply_form = ReplyForm({"name":"Someone", "email":"someone@email.com", "comment":"I am a reply", "parent_comment":comment})
        self.assertTrue(reply_form.is_valid())  
        reply = reply_form.save()

        self.assertEqual(reply.name,"Someone")
        self.assertEqual(reply.email, "someone@email.com")
        self.assertEqual(reply.comment, "I am a reply")
    
    def test_new_recipient_is_added_to_parent_comment_recipients_list_when_new_person_replies(self):
        comment = self.comment
        ReplyFactory(name="Someone", email="someone@email.com", comment="I am a reply", parent_comment=comment)
        self.assertEqual(comment.recipients.all().count(), 2)

    def test_reply_form_is_not_valid_when_blank_data(self):
        reply_form = ReplyForm({})
        self.assertFalse(reply_form.is_valid())  

        reply_form = CommentForm({"name":"Someone",})  
        self.assertFalse(reply_form.is_valid())   
        self.assertEqual(reply_form.errors, {
            'email': ['This field is required.'],
            'comment': ['This field is required.'],
        }) 

class TestUnsubscribeForm(TestCase):
    def test_unsubscribe_form_is_valid_when_valid_data(self):
        unsubscribe_form = UnsubscribeForm({"email": "unsubscribe@email.com"}) 
        self.assertTrue(unsubscribe_form.is_valid())
        self.assertEqual(unsubscribe_form.cleaned_data['email'], "unsubscribe@email.com")

    def test_unsubscribe_form_is_not_valid_when_blank_data(self):
        unsubscribe_form = UnsubscribeForm({}) 
        self.assertFalse(unsubscribe_form.is_valid())

