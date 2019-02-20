from django.shortcuts import redirect
from django.shortcuts import render
from .models import Post, Bid
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .forms import PostForm, ConfPost, UserCreationForm, EditUserForm, BidForm
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

from django.contrib.postgres.search import SearchVector
import sys
import requests
from django.core.mail import send_mail
from mysite import settings
from django.contrib import messages

from django.utils import translation

@login_required
def make_bid(request, pk):
    if "selected_language" not in request.session:
        request.session["selected_language"] = "en"
    translation.activate(request.session["selected_language"])
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = BidForm(data = request.POST, post = post, user = request.user)

        old_post_version = request.POST.get('auction_version', '')

        if int(old_post_version) != post.version:
            messages.add_message(request, messages.INFO, 'The auction has been updated')
            return render(request, 'blog/make_bid.html', {'form': form, 'post': post})

        if form.is_valid():
            print("is valid")
            #getting the bids for the current post before saving
            bids = Bid.objects.filter(post__title = post.title).all()
            bid = form.save(commit=False)
            post.version +=1
            bid.save()

            subject = "A New Bid Has Been Made"
            message = "A new bid has been made on item " + post.title + " by " + str(request.user)

            from_email = settings.EMAIL_HOST_USER

            if len(bids) == 0:
                #sending mail to person whose post it is, person who made bid
                to_list = [bid.post.author.email, request.user.email]
            if len(bids) > 0:

                bid_old_user = bids[len(bids)-1].author
                #sending mail to person whose post it is, person who made bid, person who had the bid before
                to_list = [bid.post.author.email, request.user.email, bid_old_user.email]

            send_mail(subject, message, from_email, to_list, fail_silently = True)
            return redirect('/')

    else:
        form = BidForm(post = post, user = request.user)
    return render(request, 'blog/make_bid.html', {'form': form, 'post': post})

@login_required
def edit_user(request):
    if "selected_language" not in request.session:
        request.session["selected_language"] = "en"
    translation.activate(request.session["selected_language"])
    user = request.user
    if request.method == "POST":
        form = EditUserForm(user = request.user, data = request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            #print(cleaned_data)
            user = form.save(commit=False)
            user.save()
            return redirect('/')
    else:
        form = EditUserForm(user = request.user)
    return render(request, 'blog/edit_user.html', {'form': form})

def signup(request):
    if "selected_language" not in request.session:
        request.session["selected_language"] = "en"
    translation.activate(request.session["selected_language"])
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'blog/signup.html', {'form': form})


def post_list(request):

    languages = ["en", "sv", "fi"]
    if "selected_language" not in request.session:
        request.session["selected_language"] = "en"

    currencies = ["USD", "EUR", "GBP", "SEK"]
    option = "EUR"
    if "selected_currency" not in request.session:
        request.session["selected_currency"] = "EUR"

    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')

    if request.method == "POST":
        request.session["selected_language"] = request.POST.get('selected_language', '')

        temp_search = request.POST.get('search_text', '')
        temp_posts = Post.objects.filter(title__icontains=temp_search).all()
        for post in temp_posts:
            #print(post.title)
            posts = temp_posts

        temp_currency = request.POST.get('currency', '')
        if(temp_currency == "EUR" or temp_currency =="USD" or temp_currency =="SEK" or temp_currency =="GBP"):
            request.session["selected_currency"] = temp_currency

        change_currency(posts, request.session["selected_currency"])

    translation.activate(request.session["selected_language"])
    return render(request, 'blog/post_list.html', {'posts': posts, 'currencies' : currencies, 'selected_currency' : request.session["selected_currency"], 'languages' : languages, 'selected_language' : request.session["selected_language"], 'user': request.user})

def change_currency(posts, currency):
    if(currency != "EUR"):
        curr_rate = get_currency_rate("EUR", currency)
        for post in posts:
            post.price = float(post.price) * curr_rate
            post.price = float("{0:.2f}".format(post.price))
    else:
        return

def post_search(field_name):

    if field_name.startswith('^'):
        return "%s__istartswith" % field_name[1:]
    elif field_name.startswith('='):
        return "%s__iexact" % field_name[1:]
    elif field_name.startswith('@'):
        return "%s__search" % field_name[1:]
    else:
        return "%s__icontains" % field_name

def post_detail(request, pk):
    if "selected_language" not in request.session:
        request.session["selected_language"] = "en"
    translation.activate(request.session["selected_language"])
    post = get_object_or_404(Post, pk=pk)
    if post.is_banned and not request.user.is_superuser:
        return HttpResponseNotFound('<h1>The Auction Has Been Banned</h1>')
    else:
        if request.method == 'POST':
            if 'ban_auction' in request.POST:
                ban_auction(post)
                #post.is_banned = True
                #post.save()


        return render(request, 'blog/post_detail.html', {'post': post})

def ban_auction(post):

    post.is_banned = True
    post.save()
    subject = "Auction Listing Has Been Banned"
    message = "The auction listing for " + post.title + " has been banned for not complying with the terms."

    from_email = settings.EMAIL_HOST_USER
    bids = Bid.objects.filter(post__title = post.title).all()
    to_list = [post.author.email]
    for bid in bids:
        to_list.append(bid.author.email)

    send_mail(subject, message, from_email, to_list, fail_silently = True)

def get_currency_rate(currency, rate_in):
    #for better solution use some exchange rate API
    if rate_in == "USD":
        return 1.13
    elif rate_in =="GBP":
        return 0.88
    elif rate_in =="SEK":
        return 10.49

    return 1

@login_required
def post_new(request):
    if "selected_language" not in request.session:
        request.session["selected_language"] = "en"
    translation.activate(request.session["selected_language"])
    if request.method == "POST":
        ##option = request.POST.get('option', '')
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            form = ConfPost(request.POST)
            post.deadline_date = post.deadline_date.strftime('%Y-%m-%d %H:%M')
            return render(request,'blog/confirm.html', {'p_form' : form, "p_title" : post.title, "p_text" : post.text,
            "p_price" : post.price, "p_deadline_date" : post.deadline_date})
            #return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def save_post(request):
    if "selected_language" not in request.session:
        request.session["selected_language"] = "en"
    translation.activate(request.session["selected_language"])
    option = request.POST.get('option', '')
    if option == 'Yes':
        p_author = request.user

        p_title = request.POST.get('p_title', '')
        p_text = request.POST.get('p_text', '')
        p_price = request.POST.get('p_price', '')
        p_deadline_date = request.POST.get('p_deadline_date', '')

        post = Post(author = p_author, title =p_title, text = p_text, price = p_price, deadline_date = p_deadline_date, published_date = timezone.now())

        #format(post.deadline_date, '%Y-%m-%d %H:%M')
        post.save()

        subject = "Your Auction Has Been Posted"
        message = "Your auction for item " + post.title + " was successfully created"
        from_email = settings.EMAIL_HOST_USER
        to_list = [post.author.email]
        send_mail(subject, message, from_email, to_list, fail_silently = True)

        return redirect('post_detail', pk=post.pk)

    else:
        return redirect('/')
        #return HttpResponseRedirect(reverse(""))

@login_required
def post_edit(request, pk):
    if "selected_language" not in request.session:
        request.session["selected_language"] = "en"
    translation.activate(request.session["selected_language"])
    post = get_object_or_404(Post, pk=pk)
    if post.is_banned:
        return HttpResponseNotFound('<h1>The Auction Has Been Banned</h1>')
    else:
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.published_date = timezone.now()
                post.version +=1
                post.save()
                return redirect('post_detail', pk=post.pk)
        else:
            form = PostForm(instance=post)
        return render(request, 'blog/post_edit.html', {'form': form})
