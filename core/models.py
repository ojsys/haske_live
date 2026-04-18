from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import User
from django.utils import timezone
import json

###############AUDIT#################
class BaseAuditModel(models.Model):
    created_by = models.ForeignKey(
        User,
        related_name='%(class)s_created',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    last_modified_by = models.ForeignKey(
        User,
        related_name='%(class)s_modified',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk:  # If this is a new object
            self.created_at = timezone.now()
        super().save(*args, **kwargs)


class HeroSlide(BaseAuditModel):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='hero_slides/')
    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Statistics(BaseAuditModel):
    title = models.CharField(max_length=255, default="Reaching Lives Across The Country")
    subtitle = models.CharField(max_length=255, default="Church Impact")
    stat_title1 = models.CharField(max_length=255, default="Our Statistics")
    stat_desc1 = models.CharField(max_length=255, default="An overview of the unreached people groups mostly in Nothern Nigeria")
    stat_title2 = models.CharField(max_length=255, default="Explore unreached people")
    stat_desc2 = models.CharField(max_length=255, default="Click on any colored state to see detailed statistics.")

    # Population Statistics
    total_population = models.IntegerField(default=0, help_text="Total estimated population")
    people_groups = models.IntegerField(default=0)
    states = models.IntegerField(default=0)
    lgas = models.IntegerField(default=0)
    wards = models.IntegerField(default=0)
    villages = models.IntegerField(default=0)
    converts = models.IntegerField(default=0, help_text="Number of converts")
    film_attendees = models.IntegerField(default=0, help_text="Number of film showing attendees")
    people_reached = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    # Additional Impact Metrics
    bible_translations = models.IntegerField(default=0, help_text="Number of Bible translations")
    active_missionaries = models.IntegerField(default=0, help_text="Number of active missionaries")
    training_sessions = models.IntegerField(default=0, help_text="Number of training sessions conducted")
    
    class Meta:
        verbose_name = "Statistics Section"
        verbose_name_plural = "Statistics Sections"
    
    def __str__(self):
        return f"Stats {self.title}"

class Achievement(BaseAuditModel):
    villages = models.IntegerField(default=0)
    villages_description = models.TextField(default="We have reached several villages so far. We continue to reach several villages with the gospel of Jesus")
    
    people_saved = models.IntegerField(default=0)
    people_saved_description = models.TextField(default="People have accepted the salvation gospel to receive Christ through our outreach")
    
    people_reached = models.IntegerField(default=0)
    people_reached_description = models.TextField(default="People have been reached with the gospel and have been discipled to walk with the professional love")
    
    states_reached = models.IntegerField(default=0)
    states_reached_description = models.TextField(default="States We have covered")
    
    lgas_reached = models.IntegerField(default=0)
    lgas_reached_description = models.TextField(default="Local Governments we have covered")
    
    wards_reached = models.IntegerField(default=0)
    wards_reached_description = models.TextField(default="Wards we have covered")
    
    people_discipled = models.IntegerField(default=0)
    people_discipled_description = models.TextField(default="People have submitted to Discipleship")
    
    people_baptized = models.IntegerField(default=0)
    people_baptized_description = models.TextField(default="People have submitted to Discipleship")
    
    started_discipleship = models.IntegerField(default=0)
    started_discipleship_description = models.TextField(default="People started our Discipleship Program")
    
    bibles_shared = models.IntegerField(default=0)
    bibles_shared_description = models.TextField(default="Bibles were shared")
    
    audiobibles_shared = models.IntegerField(default=0)
    audiobibles_description = models.TextField(default="Audio Bibles shared")
    
    sdcards_shared = models.IntegerField(default=0)
    sdcard_description = models.TextField(default="SD cards contain resources were shared")
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Achievement Stats (Updated: {self.updated_at.strftime('%Y-%m-%d')})"

    class Meta:
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"



class MinistrySection(BaseAuditModel):
    title = models.CharField(max_length=200, default="Reaching Lives Across The Country")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='ministry_section/')

    class Meta:
        verbose_name = "Ministry Section"
        verbose_name_plural = "Ministry Sections"

    def __str__(self):
        return self.title

class Ministry(BaseAuditModel):
    title = models.CharField(max_length=200)  # e.g., "WE PRAY", "WE FELLOWSHIP"
    description = models.TextField()
    icon = models.ImageField(upload_to='ministry_icons/', blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Ministries"
        ordering = ['order']

    def __str__(self):
        return self.title

class Activity(BaseAuditModel):
    """Field activity cards shown in the home-page Activities carousel."""
    title = models.CharField(max_length=200, help_text="e.g. Film Show, Discipleship, Medicals, Training")
    image = models.ImageField(upload_to='activities/', help_text="Background image for the activity card")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Activities"

    def __str__(self):
        return self.title


class Gallery(BaseAuditModel):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Galleries"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.image:
            from PIL import Image
            img = Image.open(self.image)
            self.width = img.width
            self.height = img.height
        super().save(*args, **kwargs)


class DemographicData(BaseAuditModel):

    STATE_CHOICES = [
        ('Abia', 'Abia'),
        ('Adamawa', 'Adamawa'),
        ('Akwa Ibom', 'Akwa Ibom'),        
        ('Anambra', 'Anambra'),      
        ('Bauchi', 'Bauchi'),     
        ('Bayelsa', 'Bayelsa'),      
        ('Benue', 'Benue'),
        ('Borno', 'Borno'),
        ('Cross River', 'Cross River'),
        ('Delta', 'Delta'),    
        ('Ebonyi', 'Ebonyi'),     
        ('Edo', 'Edo'),  
        ('Ekiti', 'Ekiti'),    
        ('Enugu', 'Enugu'),    
        ('FCT', 'Abuja'),
        ('Gombe', 'Gombe'),    
        ('Imo', 'Imo'),  
        ('Jigawa', 'Jigawa'),     
        ('Kaduna', 'Kaduna'),     
        ('Kano', 'Kano'),   
        ('Katsina', 'Katsina'),      
        ('Kebbi', 'Kebbi'),    
        ('Kogi', 'Kogi'),   
        ('Kwara', 'Kwara'),    
        ('Lagos', 'Lagos'),    
        ('Nasarawa', 'Nasarawa'),       
        ('Niger', 'Niger'),    
        ('Ogun', 'Ogun'),   
        ('Ondo', 'Ondo'),   
        ('Osun', 'Osun'),   
        ('Oyo', 'Oyo'),  
        ('Plateau', 'Plateau'),      
        ('Rivers', 'Rivers'),     
        ('Sokoto', 'Sokoto'),     
        ('Taraba', 'Taraba'),     
        ('Yobe', 'Yobe'),   
        ('Zamfara', 'Zamfara'), 
        ]


    state = models.CharField(max_length=50, choices=STATE_CHOICES)
    lga = models.CharField(max_length=100, verbose_name="L.G.A")
    ward = models.CharField(max_length=100)
    village = models.CharField(max_length=100)
    christian_population = models.IntegerField(verbose_name="Christian Population")
    muslim_population = models.IntegerField(verbose_name="Muslim Population")
    traditional_population = models.IntegerField(verbose_name="Traditional People Population")
    converts = models.IntegerField()
    total_village_population = models.IntegerField(verbose_name="Total Village Population")
    film_attendance = models.IntegerField()
    people_group = models.CharField(max_length=100)
    practiced_religion = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Demographic Data"
        # You might want to add indexes for frequently queried fields
        indexes = [
            models.Index(fields=['state']),
            models.Index(fields=['lga']),
        ]
        unique_together = ['state', 'lga', 'ward', 'village']

    def __str__(self):
        return f"{self.state}, {self.village}, {self.lga} "


class SiteLogo(BaseAuditModel):
    logo = models.ImageField(upload_to='logos/')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Site Logo"

    def __str__(self):
        return f"Logo updated on {self.updated_at}"
    

class Subscriber(BaseAuditModel):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email
    

#################### ABOUT PAGE MODEL ###################

class AboutPage(BaseAuditModel):
    title = models.CharField(max_length=200, default="ABOUT US")
    banner_subtitle = models.CharField(max_length=300, default="Proclaiming the Gospel to unreached people groups across Northern Nigeria since 2006.", blank=True)
    header_image = models.ImageField(upload_to='about/', help_text="Header image for about page")
    introduction = models.TextField(help_text="Main introduction text")
    ministry_goal = models.TextField(help_text="Main Goal", default="Our Goal")
    cta_heading = models.CharField(max_length=200, default="Be Part of Something Eternal", blank=True)
    cta_body = models.TextField(default="Millions remain unreached across Northern Nigeria. Every prayer, every hour of service, every gift — it all moves the needle of eternity.", blank=True)

    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"

    def __str__(self):
        return f"{self.title}"

class AboutMinistry(BaseAuditModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    image = models.ImageField(upload_to="about/min_img/", help_text="Ministry Image", null=True, blank=True)
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = "About Ministry"

    def __str__(self):
        return self.title

class MissionVision(BaseAuditModel):
    mission_title = models.CharField(max_length=200, default="Our Mission")
    mission_text = models.TextField()
    vision_title = models.CharField(max_length=200, default="Our Vision")
    vision_text = models.TextField()
    mission_image = models.ImageField(upload_to='about/', help_text="Image for Mission")
    vision_image = models.ImageField(upload_to='about/', help_text="Image for Vision")

    class Meta:
        verbose_name = "Mission and Vision"
        verbose_name_plural = "Mission and Vision"

    def __str__(self):
        return f"{self.mission_title} - {self.vision_title}"
    

class Challenge(BaseAuditModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    challenge1_title = models.CharField(max_length=200, default="Reaching the Unreached in 10/40 Window")
    challenge1_desc = models.TextField()
    challenge1_image = models.ImageField(upload_to='about/challenge/', help_text="Challenge Image")
    challenge2_title = models.CharField(max_length=200, default="Praying for the Unreached")
    challenge2_desc = models.TextField()
    challenge2_image = models.ImageField(upload_to='about/challenge/', help_text="Challenge Image")
    challenge3_title = models.CharField(max_length=200, default="Supporting Education in Nigeria")
    challenge3_desc = models.TextField()
    challenge3_image = models.ImageField(upload_to='about/challenge/', help_text="Challenge Image")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class BoardMember(BaseAuditModel):
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    bio = models.TextField()
    image = models.ImageField(upload_to='board/')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']


    def __str__(self):
        return self.name
    

################## PROJECTS PAGE ###############
class ProjectPage(BaseAuditModel):
    title = models.CharField(max_length=200, default="HASKE PROJECTS")
    header_image = models.ImageField(upload_to='projects/', help_text="Header image for projects page")
    introduction = models.TextField(help_text="Introduction text below header")

    class Meta:
        verbose_name = "Project Page"
        verbose_name_plural = "Project Page"
    
    def __str__(self):
        return self.title

class Project(BaseAuditModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/')
    order = models.IntegerField(default=0)
    
    # You might want to add these fields if they're relevant
    beneficiaries = models.IntegerField(default=0)
    location = models.CharField(max_length=200, blank=True)
    date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title

################################################
################## Volunteer ####################
class VolunteerPage(BaseAuditModel):
    title = models.CharField(max_length=200, default="VOLUNTEER")
    header_image = models.ImageField(upload_to='volunteer/', help_text="Header image")
    introduction = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Volunteer Page"
        verbose_name_plural = "Volunteer Page"


class VolunteerApplication(BaseAuditModel):
    INTEREST_CHOICES = [
        ('go_team', 'Go-Team Member'),
        ('prayer', 'Prayer Partner'),
        ('medical', 'Medical Outreach'),
        ('education', 'Education Support'),
        ('community', 'Community Development'),
        ('other', 'Other'),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    area_of_interest = models.CharField(max_length=50, choices=INTEREST_CHOICES)
    skills = models.TextField(help_text="Please list your relevant skills and experience")
    availability = models.TextField(help_text="When are you available to volunteer?")
    message = models.TextField(help_text="Additional message or questions", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.area_of_interest}"

    class Meta:
        ordering = ['-created_at']

class GoTeam(BaseAuditModel):
    title = models.CharField(max_length=200, default="Go-Teams")
    description = models.TextField()
    image = models.ImageField(upload_to='volunteer/teams/')
    

    def __str__(self):
        return self.title

class PrayerPartner(BaseAuditModel):
    title = models.CharField(max_length=200, default="Prayer Partners")
    description = models.TextField()
    image = models.ImageField(upload_to='volunteer/prayer/')
   
    def __str__(self):
        return self.title

class GiveSection(BaseAuditModel):
    title = models.CharField(max_length=200, default="Give")
    description = models.TextField()
    image = models.ImageField(upload_to='volunteer/give/')
    

    def __str__(self):
        return self.title

#################################################

#################  MEDIA  #######################



class BlogPost(BaseAuditModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    featured_image = models.ImageField(upload_to='blog/')
    content = CKEditor5Field()
    excerpt = models.TextField(help_text="Short description for preview", max_length=300)
    author = models.CharField(max_length=100)
    published_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    
    # Add these new fields
    created_by = models.ForeignKey(
        User,
        related_name='blog_posts_created',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    last_modified_by = models.ForeignKey(
        User,
        related_name='blog_posts_modified',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    
    class Meta:
        ordering = ['-published_date']
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('blog-detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.title


class BlogImage(BaseAuditModel):
    blog_post = models.ForeignKey(BlogPost, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blog/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']


class YouTubeVideo(BaseAuditModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_id = models.CharField(max_length=20, help_text="YouTube video ID from URL")
    published_date = models.DateTimeField()
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-published_date']
        
    def __str__(self):
        return self.title
    
    @property
    def embed_url(self):
        return f"https://www.youtube.com/embed/{self.video_id}"

class SpotifyPodcast(BaseAuditModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    spotify_id = models.CharField(max_length=100, help_text="Spotify episode/track ID")
    published_date = models.DateTimeField()
    duration = models.CharField(max_length=10, help_text="Duration in format MM:SS")
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-published_date']
        
    def __str__(self):
        return self.title

class MediaPage(BaseAuditModel):
    title = models.CharField(max_length=200, default="Media Center")
    header_image = models.ImageField(upload_to='media/')
    blog_section_title = models.CharField(max_length=200, default="Latest Blog Posts")
    youtube_section_title = models.CharField(max_length=200, default="Video Messages")
    podcast_section_title = models.CharField(max_length=200, default="Audio Messages")
    
    class Meta:
        verbose_name = "Media Page"
        verbose_name_plural = "Media Page"
        
    def __str__(self):
        return self.title

#################################################

##################  Contact   #################

class ContactSubmission(BaseAuditModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"
    
#################################################

################# Donations #####################
class DonationPage(BaseAuditModel):
    title = models.CharField(max_length=200, default="GIVE")
    header_image = models.ImageField(upload_to='donations/')
    description = models.TextField()
    bank_name = models.CharField(max_length=100, default="Zenith Bank Plc.")
    
    class Meta:
        verbose_name = "Donation Page"
        verbose_name_plural = "Donation Page"

    def __str__(self):
        return f"{self.title}"

class BankAccount(BaseAuditModel):
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    account_name = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=20, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)  # e.g., "MAIN ACCOUNT", "HUMANITARIAN"
    
    def __str__(self):
        return f"{self.account_number} - {self.description}"

#################################################


# ============================================================
#  WORDPRESS-LIKE PAGE BUILDER
# ============================================================

class Page(models.Model):
    """Admin-managed custom pages — like WordPress pages."""
    title       = models.CharField(max_length=200)
    nav_label   = models.CharField(max_length=100, blank=True, help_text="Label shown in navigation (defaults to title)")
    slug        = models.SlugField(unique=True, blank=True)
    meta_description = models.TextField(blank=True, help_text="SEO description")
    header_image     = models.ImageField(upload_to='pages/', blank=True, null=True, help_text="Banner image for the page header")
    is_published     = models.BooleanField(default=True)
    show_header      = models.BooleanField(default=True, help_text="Show the title/banner at the top of the page. Uncheck when the page starts with a Hero section.")
    show_in_nav      = models.BooleanField(default=False, help_text="Add this page to the main navigation bar")
    nav_order        = models.IntegerField(default=0, help_text="Sort order in navigation")
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nav_order', 'title']
        verbose_name = "Custom Page"
        verbose_name_plural = "Custom Pages"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('custom_page', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class PageSection(models.Model):
    """A content block within a custom page.
    Each section has a type that determines how it is rendered."""

    SECTION_TYPES = [
        ('hero',        'Hero Banner'),
        ('text',        'Text Block'),
        ('image_text',  'Image + Text'),
        ('cards',       'Cards Grid'),
        ('stats',       'Impact Statistics'),
        ('cta',         'Call to Action'),
        ('gallery',     'Image Gallery'),
        ('video',       'Video Embed'),
        ('team',        'Team / Board'),
        ('newsletter',  'Newsletter Signup'),
        ('map',         'Interactive Map'),
        ('accordion',   'FAQ / Accordion'),
    ]

    BACKGROUND_CHOICES = [
        ('white',  'White'),
        ('cream',  'Warm Cream'),
        ('gray',   'Light Gray'),
        ('navy',   'Dark Navy'),
        ('gold',   'Gold'),
        ('green',  'Forest Green'),
    ]

    IMAGE_POSITION = [
        ('right', 'Image on Right'),
        ('left',  'Image on Left'),
    ]

    page         = models.ForeignKey(Page, related_name='sections', on_delete=models.CASCADE)
    section_type = models.CharField(max_length=30, choices=SECTION_TYPES, default='text')
    order        = models.IntegerField(default=0)

    # Content
    title    = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=400, blank=True)
    body     = CKEditor5Field(blank=True)
    image    = models.ImageField(upload_to='pages/sections/', blank=True, null=True)
    image_position = models.CharField(max_length=10, choices=IMAGE_POSITION, default='right')

    # CTA
    button_text  = models.CharField(max_length=100, blank=True)
    button_url   = models.CharField(max_length=200, blank=True)
    button2_text = models.CharField(max_length=100, blank=True, verbose_name="Second button text")
    button2_url  = models.CharField(max_length=200, blank=True, verbose_name="Second button URL")

    # Style
    background = models.CharField(max_length=20, choices=BACKGROUND_CHOICES, default='white')
    css_class  = models.CharField(max_length=200, blank=True, help_text="Extra CSS classes")
    is_visible = models.BooleanField(default=True)

    # Flexible extra data (JSON) — for accordion items, extra stats, etc.
    extra_data = models.TextField(blank=True, help_text=(
        'JSON data for complex sections. '
        'Accordion: [{"question":"...", "answer":"..."}]. '
        'Extra stats: [{"number":"...","label":"..."}].'
    ))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Page Section"
        verbose_name_plural = "Page Sections"

    def __str__(self):
        return f"{self.page.title} — {self.get_section_type_display()} (#{self.order})"

    def get_extra_data(self):
        """Parse extra_data JSON safely."""
        try:
            return json.loads(self.extra_data) if self.extra_data else []
        except (json.JSONDecodeError, ValueError):
            return []


class PageSectionCard(models.Model):
    """Individual cards for a 'cards' section."""
    section  = models.ForeignKey(PageSection, related_name='cards', on_delete=models.CASCADE)
    icon     = models.CharField(max_length=100, blank=True, help_text="Font Awesome class e.g. fas fa-cross")
    image    = models.ImageField(upload_to='pages/cards/', blank=True, null=True)
    title    = models.CharField(max_length=200)
    body     = models.TextField(blank=True)
    link_text= models.CharField(max_length=100, blank=True)
    link_url = models.CharField(max_length=200, blank=True)
    order    = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.section} — {self.title}"




