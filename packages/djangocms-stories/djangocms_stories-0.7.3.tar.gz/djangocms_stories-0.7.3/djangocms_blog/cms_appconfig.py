from cms.apphook_pool import apphook_pool
from django.db import models
from django.urls import Resolver404, resolve
from django.utils.translation import get_language_from_request, gettext_lazy as _, override
from filer.models import ThumbnailOption
from parler.models import TranslatableModel, TranslatedFields

from .settings import MENU_TYPE_COMPLETE

config_defaults = {
    "default_image_full": None,
    "default_image_thumbnail": None,
    "url_patterns": "full_date",
    "use_placeholder": True,
    "use_abstract": True,
    "use_related": 1,
    "set_author": True,
    "paginate_by": 20,
    "template_prefix": "",
    "menu_structure": MENU_TYPE_COMPLETE,
    "menu_empty_categories": True,
    "sitemap_changefreq": "monthly",
    "sitemap_priority": "0.5",
    "object_type": "article",
    "og_type": "article",
    "og_app_id": None,
    "og_profile_id": None,
    "og_publisher": None,
    "og_author_url": None,
    "og_author": None,
    "twitter_type": None,
    "twitter_site": None,
    "twitter_author": None,
    "gplus_type": None,
    "gplus_author": "get_author_schemaorg",
    "send_knock_create": False,
    "send_knock_update": False,
}


class BlogConfig(TranslatableModel):
    """

    Class representing a blog configuration.

    This class inherits from TranslatableModel.

    Attributes:
        type (models.CharField): Represents the type of the blog config.
        namespace (models.CharField): Represents the namespace of the instance.
        translations (TranslatedFields): Represents the translated fields of the blog config.
        default_image_full (models.ForeignKey): Represents the default size of full images.
        default_image_thumbnail (models.ForeignKey): Represents the default size of thumbnail images.
        url_patterns (models.CharField): Represents the structure of permalinks.
        use_placeholder (models.BooleanField): Represents whether to use placeholder and plugins for article body.
        use_abstract (models.BooleanField): Represents whether to use abstract field.
        use_related (models.SmallIntegerField): Represents whether to enable related posts.
        urlconf (models.CharField): Represents the URL config.
        set_author (models.BooleanField): Represents whether to set author by default.
        paginate_by (models.SmallIntegerField): Represents the number of articles per page for pagination.
        template_prefix (models.CharField): Represents the alternative directory to load the blog templates from.
        menu_structure (models.CharField): Represents the menu structure.
        menu_empty_categories (models.BooleanField): Represents whether to show empty categories in menu.
        sitemap_changefreq (models.CharField): Represents the changefreq attribute for sitemap items.
        sitemap_priority (models.DecimalField): Represents the priority attribute for sitemap items.
        object_type (models.CharField): Represents the object type.
        og_type (models.CharField): Represents the Facebook type.
        og_app_id (models.CharField): Represents the Facebook application ID.
        og_profile_id (models.CharField): Represents the Facebook profile ID.
        og_publisher (models.CharField): Represents the Facebook page URL.
        og_author_url (models.CharField): Represents the Facebook author URL.
        og_author (models.CharField): Represents the Facebook author.
        twitter_type (models.CharField): Represents the Twitter type field.
        twitter_site (models.CharField): Represents the Twitter site handle.
        twitter_author (models.CharField): Represents the Twitter author handle.
        gplus_type (models.CharField): Represents the Schema.org object type.
        gplus_author (models.CharField): Represents the Schema.org author name abstract field.

    """

    class Meta:
        verbose_name = _("blog config")
        verbose_name_plural = _("blog configs")

    type = models.CharField(
        verbose_name=_("type"),
        max_length=100,
    )
    namespace = models.CharField(
        verbose_name=_("instance namespace"),
        default=None,
        max_length=100,
        unique=True,
    )
    translations = TranslatedFields(
        app_title=models.CharField(_("application title"), max_length=200, default="blog"),
        object_name=models.CharField(_("object name"), max_length=200, default="Article"),
    )

    #: Default size of full images
    default_image_full = models.ForeignKey(
        ThumbnailOption,
        related_name="+",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("default size of full images"),
        help_text=_("If left empty the image size will have to be set for every newly created post."),
    )
    #: Default size of thumbnail images
    default_image_thumbnail = models.ForeignKey(
        ThumbnailOption,
        related_name="+",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("default size of thumbnail images"),
        help_text=_("If left empty the thumbnail image size will have to be set for every newly created post."),
    )
    #: Structure of permalinks (get_absolute_url); see :ref:`AVAILABLE_PERMALINK_STYLES <AVAILABLE_PERMALINK_STYLES>`
    url_patterns = models.CharField(
        max_length=12,
        verbose_name=_("Permalink structure"),
        blank=True,
        default=config_defaults["url_patterns"],
        choices=[
            ("full_date", "Full date"),
            ("short_date", "Year /  Month"),
            ("category", "Category"),
            ("slug", "Just slug"),
        ],
    )
    #: Use placeholder and plugins for article body (default: :ref:`USE_PLACEHOLDER <USE_PLACEHOLDER>`)
    use_placeholder = models.BooleanField(
        verbose_name=_("Use placeholder and plugins for article body"),
        default=config_defaults["use_placeholder"],
    )
    #: Use abstract field (default: :ref:`USE_ABSTRACT <USE_ABSTRACT>`)
    use_abstract = models.BooleanField(verbose_name=_("Use abstract field"), default=config_defaults["use_abstract"])
    #: Enable related posts (default: :ref:`USE_RELATED <USE_RELATED>`)
    use_related = models.SmallIntegerField(
        verbose_name=_("Enable related posts"),
        default=config_defaults["use_related"],
        choices=(
            (0, _("No")),
            (1, _("Yes, from this blog config")),
            (2, _("Yes, from this site")),
        ),
    )
    #: Set author by default (default: :ref:`AUTHOR_DEFAULT <AUTHOR_DEFAULT>`)
    set_author = models.BooleanField(
        verbose_name=_("Set author by default"),
        default=config_defaults["set_author"],
    )
    #: When paginating list views, how many articles per page? (default: :ref:`PAGINATION <PAGINATION>`)
    paginate_by = models.SmallIntegerField(
        verbose_name=_("Paginate size"),
        null=True,
        default=config_defaults["paginate_by"],
        help_text=_("When paginating list views, how many articles per page?"),
    )
    #: Alternative directory to load the blog templates from (default: "")
    template_prefix = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name=_("Template prefix"),
        help_text=_("Alternative directory to load the blog templates from"),
    )
    #: Menu structure (default: ``MENU_TYPE_COMPLETE``, see :ref:`MENU_TYPES <MENU_TYPES>`)
    menu_structure = models.CharField(
        max_length=200,
        choices=(
            ('complete', 'Categories and posts'),
            ('categories', 'Categories only'),
            ('posts', 'Posts only'),
            ('none', 'None'),
        ),
        default=MENU_TYPE_COMPLETE,
        verbose_name=_("Menu structure"),
        help_text=_("Structure of the django CMS menu"),
    )
    #: Show empty categories in menu (default: :ref:`MENU_EMPTY_CATEGORIES <MENU_EMPTY_CATEGORIES>`)
    menu_empty_categories = models.BooleanField(
        verbose_name=_("Show empty categories in menu"),
        default=True,
        help_text=_("Show categories with no post attached in the menu"),
    )
    #: Sitemap changefreq (default: :ref:`SITEMAP_CHANGEFREQ_DEFAULT <SITEMAP_CHANGEFREQ_DEFAULT>`,
    #: see: :ref:`SITEMAP_CHANGEFREQ <SITEMAP_CHANGEFREQ>`)
    sitemap_changefreq = models.CharField(
        max_length=12,
        choices=(
            ('always', 'always'),
            ('hourly', 'hourly'),
            ('daily', 'daily'),
            ('weekly', 'weekly'),
            ('monthly', 'monthly'),
            ('yearly', 'yearly'),
            ('never', 'never')
        ),
        default="monthly",
        verbose_name=_("Sitemap changefreq"),
        help_text=_("Changefreq attribute for sitemap items"),
    )
    #: Sitemap priority (default: :ref:`SITEMAP_PRIORITY_DEFAULT <SITEMAP_PRIORITY_DEFAULT>`)
    sitemap_priority = models.DecimalField(
        decimal_places=3,
        max_digits=5,
        default="0.5",
        verbose_name=_("Sitemap priority"),
        help_text=_("Priority attribute for sitemap items"),
    )
    #: Object type (default: :ref:`TYPE <TYPE>`, see :ref:`TYPES <TYPES>`)
    object_type = models.CharField(
        max_length=200,
        blank=True,
        choices=(('Article', 'Article'), ('Website', 'Website')),
        default='Article',
        verbose_name=_("Object type"),
    )
    #: Facebook type (default: :ref:`FB_TYPE <FB_TYPE>`, see :ref:`FB_TYPES <FB_TYPES>`)
    og_type = models.CharField(
        max_length=200,
        verbose_name=_("Facebook type"),
        blank=True,
        choices=(('Article', 'Article'), ('Website', 'Website')),
        default='Article',
    )
    #: Facebook application ID (default: :ref:`FB_PROFILE_ID <FB_PROFILE_ID>`)
    og_app_id = models.CharField(
        max_length=200, verbose_name=_("Facebook application ID"), blank=True, default=""
    )
    #: Facebook profile ID (default: :ref:`FB_PROFILE_ID <FB_PROFILE_ID>`)
    og_profile_id = models.CharField(
        max_length=200, verbose_name=_("Facebook profile ID"), blank=True, default=""
    )
    #: Facebook page URL (default: :ref:`FB_PUBLISHER <FB_PUBLISHER>`)
    og_publisher = models.CharField(
        max_length=200, verbose_name=_("Facebook page URL"), blank=True, default=""
    )
    #: Facebook author URL (default: :ref:`FB_AUTHOR_URL <FB_AUTHOR_URL>`)
    og_author_url = models.CharField(
        max_length=200, verbose_name=_("Facebook author URL"), blank=True, default="get_author_url"
    )
    #: Facebook author (default: :ref:`FB_AUTHOR <FB_AUTHOR>`)
    og_author = models.CharField(
        max_length=200, verbose_name=_("Facebook author"), blank=True, default="get_author_name"
    )
    #: Twitter type field (default: :ref:`TWITTER_TYPE <TWITTER_TYPE>`)
    twitter_type = models.CharField(
        max_length=200,
        verbose_name=_("Twitter type"),
        blank=True,
        choices=(
            ('summary', 'Summary Card'),
            ('summary_large_image', 'Summary Card with Large Image'),
            ('product', 'Product'),
            ('photo', 'Photo'),
            ('player', 'Player'),
            ('app', 'App')
        ),
        default='summary',
    )
    #: Twitter site handle (default: :ref:`TWITTER_SITE <TWITTER_SITE>`)
    twitter_site = models.CharField(
        max_length=200, verbose_name=_("Twitter site handle"), blank=True, default=""
    )
    #: Twitter author handle (default: :ref:`TWITTER_AUTHOR <TWITTER_AUTHOR>`)
    twitter_author = models.CharField(
        max_length=200, verbose_name=_("Twitter author handle"), blank=True, default="get_author_twitter"
    )
    #: Schema.org object type (default: :ref:`SCHEMAORG_TYPE <SCHEMAORG_TYPE>`)
    gplus_type = models.CharField(
        max_length=200,
        verbose_name=_("Schema.org type"),
        blank=True,
        choices=(
            ('Article', 'Article'),
            ('Blog', 'Blog'),
            ('WebPage', 'Page'),
            ('WebSite', 'WebSite'),
            ('Event', 'Event'),
            ('Product', 'Product'),
            ('Place', 'Place'),
            ('Person', 'Person'),
            ('Book', 'Book'),
            ('LocalBusiness', 'LocalBusiness'),
            ('Organization', 'Organization'),
            ('Review', 'Review')
        ),
        default="Blog",
    )
    #: Schema.org author name abstract field (default: :ref:`SCHEMAORG_AUTHOR <SCHEMAORG_AUTHOR>`)
    gplus_author = models.CharField(
        max_length=200, verbose_name=_("Schema.org author name"), blank=True, default='get_author_schemaorg'
    )
    #: Send notifications on post update. Require channels integration
    send_knock_create = models.BooleanField(
        verbose_name=_("Send notifications on post publish"),
        default=False,
        help_text=_("Emits a desktop notification -if enabled- when publishing a new post"),
    )
    #: Send notifications on post update. Require channels integration
    send_knock_update = models.BooleanField(
        verbose_name=_("Send notifications on post update"),
        default=False,
        help_text=_("Emits a desktop notification -if enabled- when editing a published post"),
    )

    def get_app_title(self):
        return getattr(self, "app_title", _("untitled"))

    def save(self, *args, **kwargs):
        """Delete menu cache upon safe"""
        from menus.menu_pool import menu_pool

        menu_pool.clear(all=True)
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete menu cache upon delete"""
        from menus.menu_pool import menu_pool

        menu_pool.clear(all=True)
        return super().delete(*args, **kwargs)

    @property
    def schemaorg_type(self):
        """Compatibility shim to fetch data from legacy gplus_type field."""
        return self.gplus_type

    def __str__(self):
        try:
            return f"{self.namespace}: {self.get_app_title()} / {self.object_name}"
        except Exception as e:
            return str(e)


def get_app_instance(request):
    """
    Return current app instance namespace and config
    """
    namespace, config = "", None
    if getattr(request, "current_page", None) and request.current_page.application_urls:
        app = apphook_pool.get_apphook(request.current_page.application_urls)
        if app and app.app_config:
            try:
                config = None
                with override(get_language_from_request(request, check_path=True)):
                    if hasattr(request, "toolbar") and hasattr(request.toolbar, "request_path"):
                        path = request.toolbar.request_path  # If v4 endpoint take request_path from toolbar
                    else:
                        path = request.path_info
                    namespace = resolve(path).namespace
                    config = app.get_config(namespace)
            except Resolver404:
                pass
    return namespace, config
