from django.db import models
from django.urls import reverse
  
class Post(models.Model):
    title    = models.CharField(max_length=120)
    body     = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    # each post has a set of categories 
    categories = models.ManyToManyField('Category',
                                         related_name= 'posts')
    slug = models.SlugField(null=True)

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('blog:post_detail_view', kwargs={'slug': self.slug})    

class Comment(models.Model):
    name  = models.CharField(max_length=60)
    email = models.EmailField()
    comment  = models.TextField()
    # each comment has a post object which it belogs to.
    post = models.ForeignKey('Post', 
                              null=True, 
                              on_delete=models.CASCADE)                         
    created_on = models.DateTimeField(auto_now_add=True)
    # when it's a reply parent_comment must hold the parent comment's id,
    # it's null when it's a comment, not a reply.
    parent_comment = models.ForeignKey('self', 
                                        null=True, 
                                        blank=True, 
                                        related_name='replies', 
                                        on_delete=models.CASCADE,)
    # each comment has a list of recipients so when someone one comments on a post.
    # they get added to the recipients list so that they get notified,
    # when someone replies to thier comment,
    recipients = models.ManyToManyField('Recipient', 
                                        related_name= 'comments',) 

    class Meta:
        ordering = ('created_on',)
     
    def __str__(self):
        return self.comment

class Recipient(models.Model):
    recipient_email = models.EmailField()

    def __str__(self):
        return self.recipient_email

class Category(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category_index_view', kwargs={'category':self.name})    
  

