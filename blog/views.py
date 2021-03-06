from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import send_mail
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from .models import Post, Comment
from .forms import EmailForm, CommentForm, SearchForm


def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 5)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {
        'posts': posts,
        'page': page,
    }
    return render(request, 'blog/post/list.html', context)


def post_detail(request, year, month, day, post_slug):
    post = get_object_or_404(Post, status='published',
                             slug=post_slug,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.all()
    new_comment = None
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
    }
    return render(request, 'blog/post/detail.html', context)


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url} \n\n{cd['name']}'s comments {cd['comments']}"
            send_mail(subject, message, 'raju@blog.com', [cd['to']])
            sent = True
    else:
        form = EmailForm()
    context = {'post': post,
               'sent': sent,
               'form': form}
    return render(request, 'blog/post/share.html', context)


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            search_vector = SearchVector('title', 'body')
            query = form.cleaned_data.get('query')
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                search=SearchVector('title', 'body'), rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by('-rank')
    context = {'form': form,
               'query': query,
               'results': results}
    return render(request, 'blog/post/search.html', context)
