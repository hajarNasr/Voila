import factory
from blog.models import Post, Category, Comment, Recipient
from datetime import datetime

class CategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Category 
    name="a_category"     

class PostFactory(factory.DjangoModelFactory):
    class Meta:
        model = Post
        
    title="post title"
    body="this is the body of a post"
    pub_date= datetime.now()
    slug="post-title" 
    
    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for category in extracted:
                self.categories.add(category)

class CommentFactory(factory.DjangoModelFactory):
    class Meta:
        model =  Comment

    name = "commenter"
    email = "comm@email.com" 
    comment = "i am a comment"   
    post = factory.SubFactory(PostFactory)
    
    @factory.post_generation
    def recipients(self, create, extracted, **kwargs):
        if create:
            if self.email not in [recipient.email for recipient in self.recipients.all()]:
               recipient = RecipientFactory(recipient_email=self.email)
               self.recipients.add(recipient)

class ReplyFactory(factory.DjangoModelFactory):
    class Meta:
        model =  Comment

    name = "commenter"
    email = "E@email.com" 
    comment = "i am a reply"   
    parent_comment = factory.SubFactory(CommentFactory)

    @factory.post_generation
    def recipients(self, create, extracted, **kwargs):
        if create:
            if self.email not in [recipient.recipient_email for recipient in self.parent_comment.recipients.all()]:
               recipient = RecipientFactory(recipient_email=self.email)
               self.parent_comment.recipients.add(recipient)

class RecipientFactory(factory.DjangoModelFactory):
    class Meta:
        model = Recipient
    recipient_email = "recipient@email.com"    
   
