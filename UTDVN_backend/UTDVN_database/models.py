from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name_plural = "People"
        ordering = ["name"]
        
    def __str__(self):
        return self.name
    
class Publisher(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    
class Thesis(models.Model):
    class Language(models.TextChoices):
        ENGLISH = 'en', _('English')
        VIETNAMESE = 'vi', _('Vietnamese')
        UNKNOWN = '', _('Unknown')
    
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='author')
    advisor = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='advisor')
    pub_year = models.PositiveSmallIntegerField(blank=True, null=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    abstract = models.TextField()
    uri = models.URLField()
    file_url = models.URLField()
    language = models.CharField(max_length=10, choices=Language.choices, default=Language.UNKNOWN)
    keywords = models.CharField(max_length=500)
    
    class Meta:
        verbose_name_plural = "Theses"
        ordering = ["title"]
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'], name='unique_thesis'),
            models.CheckConstraint(check=models.Q(pub_year__lte=timezone.now().year), name='pub_year_lte_now'),
        ]
        
    def __str__(self):
        return self.title