from tabnanny import verbose
from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django_fsm import FSMField, transition

class CustomAccountManager(BaseUserManager):
    # This class let us define our own custom sign up and sign in methods.

    def create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, username, password, **extra_fields)

class MyUser(AbstractBaseUser, PermissionsMixin):
    # Note: You can'T call the model User as this is a built-in model.
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)

    is_staff = models.BooleanField(_('staff'), default=False)
    is_active = models.BooleanField(_('active'), default=True)

    # This tells django to use the email as the main sign in field.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        "username"
    ]

    objects = CustomAccountManager()

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

class BlogPostStateChoices(models.TextChoices):
    DRAFT = ('draft', _('Draft'))
    WAITING_APPOROVAL = ('waiting approval', _('Waiting Approval'))
    PUBLISHED = ('published', _('Published'))

class BlogPost(models.Model):
    title = models.CharField(verbose_name="Title", max_length=255)
    content = models.TextField(verbose_name="Content")
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    state = FSMField(
        default=BlogPostStateChoices.DRAFT,
        choices=BlogPostStateChoices.choices
    )

    @transition(
        field=state,
        source=BlogPostStateChoices.DRAFT,
        target=BlogPostStateChoices.WAITING_APPOROVAL,
        conditions=[lambda instance: instance.state == BlogPostStateChoices.DRAFT],
        permission=lambda instance, user: instance.author == user
    )
    def submit(self):
        print("Post needs approval " + str(self))

    # If the author edits the blog post while its waiting for approval, the state will change to draft.
    @transition(
        field=state,
        source=BlogPostStateChoices.WAITING_APPOROVAL,
        target=BlogPostStateChoices.DRAFT,
        conditions=[lambda instance: instance.state == BlogPostStateChoices.WAITING_APPOROVAL]
    )
    def edit(self):
        pass

    @transition(
        field=state,
        source=BlogPostStateChoices.WAITING_APPOROVAL,
        target=BlogPostStateChoices.PUBLISHED,
        conditions=[lambda instance: instance.state == BlogPostStateChoices.WAITING_APPOROVAL],
        permission=lambda instance, user: user.is_superuser
    )
    def approve(self):
        print("Post approved " + str(self))

    @transition(
        field=state,
        source=BlogPostStateChoices.WAITING_APPOROVAL,
        target=BlogPostStateChoices.DRAFT,
        conditions=[lambda instance: instance.state == BlogPostStateChoices.WAITING_APPOROVAL],
        permission=lambda instance, user: user.is_superuser
    )
    def dissaprove(self):
        print("Post dissaproved " + str(self))
    
    @transition(
        field=state,
        source=BlogPostStateChoices.PUBLISHED,
        target=BlogPostStateChoices.DRAFT,
        conditions=[lambda instance: instance.state == BlogPostStateChoices.PUBLISHED],
        permission=lambda instance, user: instance.author == user or user.is_superuser
    )
    def unpublish(self):
        pass

    def __str__(self):
        return self.title + " by: " + str(self.author)

    class Meta:
        verbose_name = _("Blog Post")
        verbose_name_plural = _("Blog Posts")