from importlib import resources

def get_templates_dir() -> str:
    with resources.path('vg_lib.templates', '') as templates_dir:
        return str(templates_dir)

DEFAULT_VIRTUALHOSTS_ROOT = "/var/www/html"
DEFAULT_APACHE_CONFIG = "/etc/apache2/apache2.conf"
DEFAULT_APACHE_SITES_AVAILABLE = "/etc/apache2/sites-available"
DEFAULT_APACHE_SITES_ENABLED = "/etc/apache2/sites-enabled"
DEFAULT_PHP_FPM_CONFIG_DIR = "/etc/php/8.1/fpm/pool.d"
DEFAULT_VG_TOOLS_ETC_DIR = get_templates_dir()
DEFAULT_RSYSLOG_CONFIG_DIR = "/etc/rsyslog.d"
DEFAULT_PHP_FPM_SERVICE_NAME = "php8.1-fpm.service"
DEFAULT_VG_TOOLS_VAR_DIR = "/usr/local/vg_tools/vg_management/var"
DEFAULT_LOGLEVEL = "INFO"
