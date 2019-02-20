from django_cron import CronJobBase, Schedule
from django.shortcuts import get_object_or_404
from blog.models import Post, Bid
from datetime import datetime, timedelta
from django.utils import timezone
from mysite import settings
from django.core.mail import send_mail

class MyCronJob(CronJobBase):

    RUN_EVERY_MINS = 1
    RETRY_AFTER_FAILURE_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'my_cron_job'    # a unique code

    def do(self):

        posts = Post.objects.all()
        for post in posts:
            if timezone.now() > post.deadline_date:
                bids = Bid.objects.filter(post__title = post.title).all()
                from_email = settings.EMAIL_HOST_USER
                subject = "Auction Has Ended"
                message = "The auction for item " + post.title + " has ended."
                to_list = [post.author.email]
                for bid in bids:
                    to_list.append(bid.author.email)

                send_mail(subject, message, from_email, to_list, fail_silently = True)
                post.is_banned = True #banning it for now to prevent it from showing in lists
