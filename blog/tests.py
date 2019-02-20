from django.test import TestCase
from blog.models import Post, Bid
from blog.forms import PostForm, BidForm
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone

class BidTestCaseUC6(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='abc', email='abc@abo.fi', password='abc')
        self.user2 = User.objects.create_user(
            username='abc2', email='abc2@abo.fi', password='abc2')
        self.post = Post.objects.create(author= self.user, title= 'my_title', text= 'my_text', price= 1, deadline_date= '2018-11-13 09:00')

    def test_bid_form_and_creation(self):
        #testing that the bid has to be 0.1 higher than the auction price
        form_data = {'bid': 1}
        form = BidForm(data=form_data, post=self.post, user = self.user2)
        self.assertFalse(form.is_valid())

        #testing that the user cant bid on own auction
        form_data = {'bid': 1.1}
        form = BidForm(data=form_data, post=self.post, user = self.user)
        self.assertFalse(form.is_valid())

        #testing that the form is validated using accepted values
        form_data = {'bid': 1.1}
        form = BidForm(data=form_data, post=self.post, user = self.user2)
        self.assertTrue(form.is_valid())

        #testing that the bid can be saved
        print("Before making a bid:",Bid.objects.count())
        bid = form.save(commit=False)
        bid.save()
        print("After making a bid:",Bid.objects.count())

        #testing that the site behaves as expected when adding a bid
        response = self.client.post('/post/1/make_bid/', form_data)
        self.failUnlessEqual(response.status_code, 302)
        #testing that the price has been incremented to 1.1
        self.assertTrue(self.post.price == 1.1)

class PostTestCaseUC3(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='abc', email='abc@abo.fi', password='abc')
        self.current_datetime = timezone.now()
        format(self.current_datetime, '%Y-%m-%d %H:%M')

    def test_auction_form_and_post(self):
        #testing that strings cant be entered as price
        form_data = {'title': 'my_title', 'text': 'my_text', 'price': "text", 'deadline_date': '2018-11-13 09:00'}
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())

        #testing that numbers <=0 cant be entered as price
        form_data['price'] = 0
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())

        #testing that the deadline format has to be correct
        form_data['price'] = 0.1
        form_data['deadline_date'] = "2018.11.12 07:00"
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())

        #testing that the deadline datetime has to be atleast 72h from current datetime
        form_data['deadline_date'] = self.current_datetime + timedelta(hours=71)
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())

        #testing that the form is validated as correct with accepted form values
        form_data['deadline_date'] = self.current_datetime + timedelta(hours=72, minutes=0.1) #adding some seconds to compensate test run time
        print(form_data)
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

        #testing that the auction post can be saved
        print("Before creating an auction:",Post.objects.count())
        post = form.save(commit=False)
        post.author = self.user
        post.save()
        print("After creating an auction:",Post.objects.count())

        #testing that the site behaves as expected when adding an auction
        response = self.client.post('/post/new/', form_data)
        self.failUnlessEqual(response.status_code, 302)
        response = self.client.get('/post/1/')
        print(response.content)
