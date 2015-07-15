from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'kassis_orange.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^search/', include('app_search.urls')),

    url(r'^$', 'app_search.views.search_index', name='home'),
    url(r'^search/$', 'app_search.views.search_index', name='search_index'),
    url(r'^search/results$', 'app_search.views.search_results', name='search_results'),
    url(r'^m/(?P<m_id>\d+)$', 'app_search.views.m_show', name="m_show"),
    url(r'^m/(?P<m_id>\d+)\.(?P<format>(json)|(xml))$', 'app_search.views.m_show'),
    url(r'^import_isbn$', 'app_search.views.m_import_isbn', name="m_import_isbn_ndl"),
    url(r'^import_rss$', 'app_search.views.m_import_from_ndl_rss', name="m_import_from_ndl_rss"),

    # auth (see also: http://nwpct1.hatenablog.com/entry/django-oauth-twitter-facebook-github)
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'accounts/login.jinja'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'template_name': 'accounts/logged_out.jinja'}),
    url(r'^accounts/profile/$', 'app_accounts.views.profile', name="profile"),

    # admin
    #url(r'^admin/', include(admin.site.urls)),

    # crud
    url(r'^u/$', 'app_admin.views.users', name="users"),
    url(r'^u/new$', 'app_admin.views.new_user', name="new_user"),
    url(r'^u/(?P<pk>\d+)/edit$', 'app_admin.views.edit_user', name="edit_user"),
    url(r'^u/(?P<pk>\d+)$', 'app_admin.views.user', name="user"),
    url(r'^locations/$', 'app_admin.views.locations', name="locations"),
    url(r'^locations/new$', 'app_admin.views.new_location', name="new_location"),
    url(r'^locations/(?P<pk>\d+)$', 'app_admin.views.location', name="location"),

    # checkout and checkin
    url(r'^checkouts/new$', 'app_checkout.views.new_checkout', name="new_checkout"),
    url(r'^checkouts/$', 'app_checkout.views.checkouts', name="checkouts"),
    url(r'^checkins/new$', 'app_checkout.views.new_checkin', name="new_checkin"),
    url(r'^checkins/$', 'app_checkout.views.checkins', name="checkins"),

]
