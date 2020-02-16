from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Post, Comment, Recipient
from .forms import CommentForm, ReplyForm, UnsubscribeForm
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives, get_connection, send_mail
from django.template import loader
from voila.settings import VOILA_HOST, MY_EMAIL as my_email

class IndexView(generic.ListView):
    template_name = 'blog/blog-index.html'
    context_object_name = 'posts'
    model = Post
    paginate_by = 5
    def get_queryset(self):
        ''' Return all the posts on blog ordered from newest to oldest '''
        return Post.objects.all().order_by('-pub_date')

class CategoryIndexView(generic.ListView):
    template_name = 'blog/category-index-view.html'
    context_object_name = 'posts'
    model = Post
    paginate_by = 5
    def get_queryset(self):
        '''Return every post that has <category> in its set of categories ordered from newest to oldest'''
        category = self.kwargs['category']
        return Post.objects.filter(categories__name__iexact = category).order_by('-pub_date')

class PostDetailView(generic.DetailView):
    model = Post
    template_name = "blog/post-detail.html"
    comment_form, reply_form = CommentForm(), ReplyForm()

    def get_queryset(self, **kwargs):
        ''' Return the post where post.slug=slug''' 
        slug = self.kwargs.get('slug')
        queryset = Post.objects.filter(slug=slug)
        return queryset

    def get_context_data(self, *args, **kwargs):
        ''' Return context to be passed to a template '''  
        post = self.get_queryset(**kwargs)[0]
        comments = Comment.objects.filter(post=post).order_by('created_on')
        comments_count = comments.count()
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['comments'] = comments
        context['comments_count'] = comments_count
        context['comment_form'] = self.comment_form
        '''A reply form only exists if there's at least one comment on the post.'''
        if comments_count:
           context['reply_form']  = self.reply_form
        return context

    def post(self, request, *args, **kwargs):
        ''' Hadnel the http POST method '''  
        post = self.get_queryset(**kwargs)[0]
        self.object = self.get_object()  
        comment_form = CommentForm(request.POST)
        
        if comment_form.is_valid():
            name = comment_form.cleaned_data["name"]
            email = comment_form.cleaned_data["email"]
            comment_msg= comment_form.cleaned_data["comment"]

            # check if it's a comment form or a reply form
            try:           
               parent_comment_id = int(request.POST.get('parent_comment_id'))
            except: 
               # it's a comment with no replies because the hidden input parent_comment_id wasn't submitted   
               parent_comment_id = None  
                
           
            if parent_comment_id:  # it's a reply because it has a parent id
               reply_form = ReplyForm(request.POST)
               self.save_valid_form(name, email, comment_msg, post, parent_comment_id)  
            else:
               self.save_valid_form(name, email, comment_msg, post)     
        
        return render(request, self.template_name, self.get_context_data(**kwargs))  
        
    def save_valid_form(self, name, email, comment_msg, post, parent_comment_id=None):
        comment = Comment(name=name,
                          email= email,
                          comment=comment_msg,
                         )
        if not parent_comment_id:
            # it's a comment and a comment must belong to a post
            # so we are adding it to the current post
            comment.post = post
            comment.save()
            # and we're also adding the commenter to the recipient list of the comment
            self.add_new_recipient(comment, email) 
            # An email message will be sent to my_email whenever someone comments on a post
            message = f"Someone commented on {post.get_absolute_url()}"
            send_mail("A new comment from Voila", message, my_email, [my_email], fail_silently=False)
        else:
            # when it's a reply we need to know to which comment this reply belongs
            parent_comment = Comment.objects.get(id=parent_comment_id)  
            comment.parent_comment = parent_comment 
            set_of_recipients = set(
                 recipient.recipient_email for recipient in parent_comment.recipients.all() if recipient.recipient_email != email
            )      
   
            if set_of_recipients:
                self.notify_recipients_of_new_reply(set_of_recipients, post, name, parent_comment_id)

            if email not in parent_comment.recipients.all():
                self.add_new_recipient(parent_comment, email)  

            comment.save()
            parent_comment.replies.add(comment) 

            #if not parent_comment.replies.all or not Comment.objects.all:
               # Recipient.objects.filter(recipient_email__contains="@").delete() 

    def add_new_recipient(self, parent_comment, email):
        '''Add new recipients to comments for possible future email notifications'''
        recipient = Recipient(recipient_email=email)
        recipient.save()
        parent_comment.recipients.add(recipient)  
                      
    
    def notify_recipients_of_new_reply(self, set_of_recipients, post, name, parent_comment_id):
        '''Send email notifications to all the people on the comment's recipients list'''

        subject = "A new reply from Voila"
        html_template = loader.get_template('blog/email-template.html')
        context = {
            "name": name,
            "post": post,
            "comment_id": parent_comment_id,
            "VOILA_HOST": VOILA_HOST,
        }
        text_content = "Someone replied to your comment."
        html_content = html_template.render(context)
        messages = []
        for recipient in set_of_recipients:
            msg = EmailMultiAlternatives(subject, text_content, my_email, [recipient])
            msg.attach_alternative(html_content, "text/html")
            messages.append(msg)
        return get_connection().send_messages(messages) 

def unsubscribe_from_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    email = unsubscribe(request)
    if email: 
        if comment.recipients.filter(recipient_email=email):
           # if a valid email and belongs to the recipients list of this comment
           # delete it
           comment.recipients.filter(recipient_email=email).delete() 
           return rerender_or_success(request,"success")
        else:
           # else: display an error message to let the user know that
           # the email they entered doesn't belong to the recipients list of this comment 
           messages.error(request, "The email you entered is not subscribed to any post.")
   
    return rerender_or_success(request,"rerender") 

def unsubscribe_from_all_posts(request):
    email = unsubscribe(request)
    if email:
       if email in [recipient.recipient_email for recipient in Recipient.objects.all()]:
           # if a valid email and an object of Recipient model, delete it
          Recipient.objects.filter(recipient_email=email).delete() 
          return rerender_or_success(request,"success") 
       else:
           messages.error(request, "The email you entered is not subscribed to any post.")  

    return rerender_or_success(request, "rerender")       

def unsubscribe(request): 
    if request.method == "POST":
        unsubscribe_form = UnsubscribeForm(request.POST)
        if unsubscribe_form.is_valid(): 
           recip_email = unsubscribe_form.cleaned_data['email'].lower() 
           return recip_email   

def rerender_or_success(request, msg):
    if msg == "success":
       return render(request, "blog/successfully-unsubscribed.html")
    else:
       return render(request, "blog/unsubsribe-email.html", {"unsubscribe_form": UnsubscribeForm()}) 
   




