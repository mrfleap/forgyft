import tldextract as tldextract
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned
from django.core.mail import send_mail
from django.db import models

# Create your models here.
from django.db.models import Model
from django.dispatch import receiver
from django.http import Http404
from django.urls import reverse

from forgyft import settings
from forgyftapp.messaging import broadcast_to_slack, debug_log
from forgyftapp.util import django_utils


class OnCreate:
	def onCreate(self):
		pass





class Slug(OnCreate, models.Model):
	_slug = models.SlugField(max_length=7, blank=True)

	def onCreate(self):
		super().onCreate()
		self._slug = self.slug
		self.save()

	@property
	def slug(self):
		if not self._slug:
			newSlug = django_utils.get_slug(self, length=7, underscoreSlug=True)
			self._slug = newSlug
			self.save()
		return self._slug

	@classmethod
	def fromSlug(cls, slug, case_insensitive=True):
		if case_insensitive:
			slug = slug.upper()
		obj = cls.objects.filter(_slug=slug)

		if obj.count() == 0:
			raise Http404(f"No {cls.__name__} found with the ID {str(slug)}")
		elif obj.count() > 1:
			raise MultipleObjectsReturned(f"Multiple {cls.__name__}s found with ID " + str(slug))
		else:
			listing = obj.first()

		return listing

	class Meta:
		abstract = True


class User(AbstractUser, Slug):
	email_confirmed = models.BooleanField(default=False)

	def onCreate(self):
		super().onCreate()
		self.save()

class gender:
	MALE = "MALE"
	FEMALE = "FEMALE"
	OTHER = "OTHER"

	GENDERS = ["Male", "Female", "Other"]
	GENDER_CHOICES = ((MALE, "Male"),
	                  (FEMALE, "Female"),
	                  (OTHER, "Other"))


class GiftFeedback(models.Model, OnCreate):

	rating = models.IntegerField()
	feedback = models.TextField(max_length=6000)
	bought = models.BooleanField()

	def onCreate(self):
		super().onCreate()
		fulfillUrl = settings.ABSOLUTE_URI + reverse("forgyftapp:fulfill", kwargs={"profile": self.giftee_profile.pk})
		debug_log(f"User submitted feedback for gift ideas. View it <{fulfillUrl}|here>.")
		broadcast_to_slack(f"Hey <!channel>, a user submitted feedback for gift ideas."
		                   f" View it <{fulfillUrl}|here>.")


class GifteeProfile(models.Model, OnCreate):
	name = models.TextField(max_length=150)
	gender = models.CharField(max_length=80, choices=gender.GENDER_CHOICES)
	age = models.IntegerField()
	relationship = models.TextField(max_length=6000)
	price_upper = models.IntegerField()
	interests = models.TextField(max_length=6000)
	existing_related_items = models.TextField(max_length=6000)
	extra_info = models.TextField(max_length=6000, blank=True, null=True)
	occasion = models.TextField(max_length=6000)

	published = models.BooleanField(default=False)

	emailed_about_publish = models.BooleanField(default=False)

	user = models.ForeignKey(User, on_delete=models.CASCADE)

	feedback = models.OneToOneField(GiftFeedback, on_delete=models.SET_NULL, null=True)

	@property
	def status(self):
		if self.published:
			return "Your gift ideas are ready, click on the button below to view them."
		else:
			return "We're still deciding on the perfect gifts, please check back soon."

	def submit(self, request):
		debug_log(f"Submitted gift ideas for {self.name}, as requested by {self.user.get_full_name()}")
		if not self.emailed_about_publish:
			view_url = request.build_absolute_uri(reverse("forgyftapp:request", kwargs={"profile": self.pk}))
			send_mail(f"Your gift ideas for {self.name} are ready",
			          f"To view your gift ideas click this link: {view_url}",
			          "noreply@forgyft.com",
			          [self.user.email],
			          html_message=f"To view your gift ideas click <a href=\"{view_url}\">here</a>")
			self.emailed_about_publish = True
		self.published = True
		self.save()

	def unsubmit(self):
		if self.published:
			debug_log(f"Unsubmitted gift ideas for {self.name}, as requested by {self.user.get_full_name()}")
			self.published = False
			self.save()

	def gender_string(self):
		choices = {}

		for choice in gender.GENDER_CHOICES:
			choices[choice[0]] = choice[1]

		return choices.get(self.gender)

	@property
	def admin_url(self):
		return reverse('admin:{0}_{1}_change'.format(self._meta.app_label, self._meta.model_name), args=(self.pk,))

	def __str__(self):
		return f"Giftee Profile {self.pk} for {self.name} from {self.user.get_full_name()}"

	def onCreate(self):
		super().onCreate()
		if not settings.DEBUG:
			fulfillUrl = settings.ABSOLUTE_URI + reverse("forgyftapp:fulfill", kwargs={"profile": self.pk})
			debug_log(f"User with email address \"{self.user.email}\" submitted new gift request.")
			broadcast_to_slack(f"Hey <!channel>, there was a new gift request created by {str(self.user)}. "
			                   f"Enter gift ideas <{fulfillUrl}|here>")


class GiftIdea(models.Model, OnCreate):
	idea = models.TextField()
	link = models.URLField(max_length=2400)
	image = models.URLField(max_length=2400, blank=True, null=True)
	explanation = models.TextField()
	published = models.BooleanField(default=False)
	giftee_profile = models.ForeignKey(GifteeProfile, related_name="ideas", on_delete=models.CASCADE)
	clicks = models.IntegerField(default=0)


	@property
	def domain(self):
		return tldextract.extract(self.link).domain


	def click(self):
		self.clicks += 1
		self.save()


@receiver(models.signals.post_save)
def execute_after_save(sender, instance, created, *args, **kwargs):
	if issubclass(instance.__class__, OnCreate) and created:
		instance.onCreate()