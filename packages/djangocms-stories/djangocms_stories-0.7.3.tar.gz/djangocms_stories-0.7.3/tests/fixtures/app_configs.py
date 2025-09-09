import pytest
from django.utils.translation import activate

from djangocms_stories.cms_appconfig import StoriesConfig, config_defaults

PERMALINK_TYPE_FULL_DATE = "full_date"
PERMALINK_TYPE_SHORT_DATE = "short_date"
PERMALINK_TYPE_CATEGORY = "category"
PERMALINK_TYPE_SLUG = "slug"


@pytest.fixture
def simple_w_placeholder(db):
    activate("en")
    return StoriesConfig.objects.using(db).create(**{
        **config_defaults,
        "namespace": "djangocms_stories",
        "app_title": "Test Stories",
        "object_name": "Story",
        "url_patterns": PERMALINK_TYPE_FULL_DATE,
        "use_placeholder": True,
        "template_prefix": "",
    })



@pytest.fixture
def simple_wo_placeholder(db):
    activate("en")
    return StoriesConfig.objects.using(db).create(**{
        **config_defaults,
        "namespace": "test_ns_wo_placeholder",
        "app_title": "Test Stories Without Placeholder",
        "object_name": "Short story",
        "url_patterns": PERMALINK_TYPE_CATEGORY,
        "use_placeholder": False,
        "template_prefix": "",
    })

default_config = simple_w_placeholder
