from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Post, Category, Tag, Comment, Newsletter
from django.core.mail import send_mail
from django.conf import settings


def home(request):
    """Home page with featured and recent posts"""
    featured_posts = Post.objects.filter(
        status='published',
        featured=True,
        published_at__lte=timezone.now()
    )[:3]
    
    recent_posts = Post.objects.filter(
        status='published',
        published_at__lte=timezone.now()
    ).exclude(id__in=[post.id for post in featured_posts])[:6]
    
    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0)[:5]
    
    context = {
        'featured_posts': featured_posts,
        'recent_posts': recent_posts,
        'categories': categories,
    }
    return render(request, 'blog/home.html', context)


def post_list(request):
    """List all published posts with pagination"""
    posts = Post.objects.filter(
        status='published',
        published_at__lte=timezone.now()
    )
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    paginator = Paginator(posts, 9)  # Show 9 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """Display a single post with comments"""
    post = get_object_or_404(
        Post,
        slug=slug,
        status='published',
        published_at__lte=timezone.now()
    )
    
    # Increment view count
    post.views += 1
    post.save(update_fields=['views'])
    
    # Get approved comments
    comments = post.comments.filter(is_approved=True, parent=None)
    
    # Related posts
    related_posts = Post.objects.filter(
        category=post.category,
        status='published'
    ).exclude(id=post.id)[:3]
    
    # Handle comment submission
    if request.method == 'POST':
        author = request.POST.get('author')
        email = request.POST.get('email')
        website = request.POST.get('website', '')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if author and email and content:
            parent = None
            if parent_id:
                parent = get_object_or_404(Comment, id=parent_id)
            
            Comment.objects.create(
                post=post,
                author=author,
                email=email,
                website=website,
                content=content,
                parent=parent
            )
            messages.success(request, 'Your comment has been submitted and is pending approval.')
            return redirect('blog:post_detail', slug=post.slug)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)


def category_posts(request, slug):
    """Display posts from a specific category"""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        category=category,
        status='published',
        published_at__lte=timezone.now()
    )
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category_posts.html', context)


def tag_posts(request, slug):
    """Display posts with a specific tag"""
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(
        tags=tag,
        status='published',
        published_at__lte=timezone.now()
    )
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'page_obj': page_obj,
    }
    return render(request, 'blog/tag_posts.html', context)


def about(request):
    """About page"""
    return render(request, 'blog/about.html')


def contact(request):
    """Contact page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            # Send email (configure your email settings)
            try:
                send_mail(
                    f'Contact Form: {subject}',
                    f'From: {name} <{email}>\n\n{message}',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully!')
                return redirect('blog:contact')
            except Exception as e:
                messages.error(request, 'There was an error sending your message. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'blog/contact.html')


@require_POST
def newsletter_signup(request):
    """Handle newsletter signup via AJAX"""
    email = request.POST.get('email')
    
    if not email:
        return JsonResponse({'success': False, 'message': 'Email is required'})
    
    newsletter, created = Newsletter.objects.get_or_create(
        email=email,
        defaults={'is_active': True}
    )
    
    if created:
        return JsonResponse({'success': True, 'message': 'Successfully subscribed to newsletter!'})
    elif newsletter.is_active:
        return JsonResponse({'success': False, 'message': 'Email already subscribed'})
    else:
        newsletter.is_active = True
        newsletter.save()
        return JsonResponse({'success': True, 'message': 'Successfully resubscribed to newsletter!'})


def archive(request):
    """Archive page showing posts by date"""
    posts = Post.objects.filter(
        status='published',
        published_at__lte=timezone.now()
    ).dates('published_at', 'month', order='DESC')
    
    context = {
        'archive_dates': posts,
    }
    return render(request, 'blog/archive.html', context)


def archive_month(request, year, month):
    """Show posts from a specific month"""
    posts = Post.objects.filter(
        status='published',
        published_at__year=year,
        published_at__month=month,
        published_at__lte=timezone.now()
    )
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'year': year,
        'month': month,
    }
    return render(request, 'blog/archive_month.html', context)