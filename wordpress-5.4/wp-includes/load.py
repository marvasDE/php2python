#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import cgi
    import os
    import os.path
    import copy
    import sys
    from goto import with_goto
    with open(os.getenv('PHP2PY_COMPAT', 'php_compat.py')) as f:
        exec(compile(f.read(), '<string>', 'exec'))
    # end with
    globals()['__PHP2PY_LOADED__'] = True
# end if
#// 
#// These functions are needed to load WordPress.
#// 
#// @package WordPress
#// 
#// 
#// Return the HTTP protocol sent by the server.
#// 
#// @since 4.4.0
#// 
#// @return string The HTTP protocol. Default: HTTP/1.0.
#//
def wp_get_server_protocol(*args_):
    
    protocol = PHP_SERVER["SERVER_PROTOCOL"] if (php_isset(lambda : PHP_SERVER["SERVER_PROTOCOL"])) else ""
    if (not php_in_array(protocol, Array("HTTP/1.1", "HTTP/2", "HTTP/2.0"))):
        protocol = "HTTP/1.0"
    # end if
    return protocol
# end def wp_get_server_protocol
#// 
#// Turn register globals off.
#// 
#// @since 2.1.0
#// @access private
#//
def wp_unregister_GLOBALS(*args_):
    
    #// phpcs:ignore WordPress.NamingConventions.ValidFunctionName.FunctionNameInvalid
    if (not php_ini_get("register_globals")):
        return
    # end if
    if (php_isset(lambda : PHP_REQUEST["GLOBALS"])):
        php_print("GLOBALS overwrite attempt detected")
        php_exit()
    # end if
    #// Variables that shouldn't be unset.
    no_unset = Array("GLOBALS", "_GET", "_POST", "_COOKIE", "_REQUEST", "_SERVER", "_ENV", "_FILES", "table_prefix")
    input = php_array_merge(PHP_REQUEST, PHP_POST, PHP_COOKIE, PHP_SERVER, PHP_ENV, PHP_FILES, PHP_SESSION if (php_isset(lambda : PHP_SESSION)) and php_is_array(PHP_SESSION) else Array())
    for k,v in input:
        if (not php_in_array(k, no_unset)) and (php_isset(lambda : PHP_GLOBALS[k])):
            PHP_GLOBALS[k] = None
        # end if
    # end for
# end def wp_unregister_GLOBALS
#// 
#// Fix `$_SERVER` variables for various setups.
#// 
#// @since 3.0.0
#// @access private
#// 
#// @global string $PHP_SELF The filename of the currently executing script,
#// relative to the document root.
#//
def wp_fix_server_vars(*args_):
    global PHP_SERVER
    global PHP_SELF
    php_check_if_defined("PHP_SELF")
    default_server_values = Array({"SERVER_SOFTWARE": "", "REQUEST_URI": ""})
    PHP_SERVER = php_array_merge(default_server_values, PHP_SERVER)
    #// Fix for IIS when running with PHP ISAPI.
    if php_empty(lambda : PHP_SERVER["REQUEST_URI"]) or PHP_SAPI != "cgi-fcgi" and php_preg_match("/^Microsoft-IIS\\//", PHP_SERVER["SERVER_SOFTWARE"]):
        if (php_isset(lambda : PHP_SERVER["HTTP_X_ORIGINAL_URL"])):
            #// IIS Mod-Rewrite.
            PHP_SERVER["REQUEST_URI"] = PHP_SERVER["HTTP_X_ORIGINAL_URL"]
        elif (php_isset(lambda : PHP_SERVER["HTTP_X_REWRITE_URL"])):
            #// IIS Isapi_Rewrite.
            PHP_SERVER["REQUEST_URI"] = PHP_SERVER["HTTP_X_REWRITE_URL"]
        else:
            #// Use ORIG_PATH_INFO if there is no PATH_INFO.
            if (not (php_isset(lambda : PHP_SERVER["PATH_INFO"]))) and (php_isset(lambda : PHP_SERVER["ORIG_PATH_INFO"])):
                PHP_SERVER["PATH_INFO"] = PHP_SERVER["ORIG_PATH_INFO"]
            # end if
            #// Some IIS + PHP configurations put the script-name in the path-info (no need to append it twice).
            if (php_isset(lambda : PHP_SERVER["PATH_INFO"])):
                if PHP_SERVER["PATH_INFO"] == PHP_SERVER["SCRIPT_NAME"]:
                    PHP_SERVER["REQUEST_URI"] = PHP_SERVER["PATH_INFO"]
                else:
                    PHP_SERVER["REQUEST_URI"] = PHP_SERVER["SCRIPT_NAME"] + PHP_SERVER["PATH_INFO"]
                # end if
            # end if
            #// Append the query string if it exists and isn't null.
            if (not php_empty(lambda : PHP_SERVER["QUERY_STRING"])):
                PHP_SERVER["REQUEST_URI"] += "?" + PHP_SERVER["QUERY_STRING"]
            # end if
        # end if
    # end if
    #// Fix for PHP as CGI hosts that set SCRIPT_FILENAME to something ending in php.cgi for all requests.
    if (php_isset(lambda : PHP_SERVER["SCRIPT_FILENAME"])) and php_strpos(PHP_SERVER["SCRIPT_FILENAME"], "php.cgi") == php_strlen(PHP_SERVER["SCRIPT_FILENAME"]) - 7:
        PHP_SERVER["SCRIPT_FILENAME"] = PHP_SERVER["PATH_TRANSLATED"]
    # end if
    #// Fix for Dreamhost and other PHP as CGI hosts.
    if php_strpos(PHP_SERVER["SCRIPT_NAME"], "php.cgi") != False:
        PHP_SERVER["PATH_INFO"] = None
    # end if
    #// Fix empty PHP_SELF.
    PHP_SELF = PHP_SERVER["PHP_SELF"]
    if php_empty(lambda : PHP_SELF):
        PHP_SERVER["PHP_SELF"] = php_preg_replace("/(\\?.*)?$/", "", PHP_SERVER["REQUEST_URI"])
        PHP_SELF = PHP_SERVER["PHP_SELF"]
    # end if
# end def wp_fix_server_vars
#// 
#// Check for the required PHP version, and the MySQL extension or
#// a database drop-in.
#// 
#// Dies if requirements are not met.
#// 
#// @since 3.0.0
#// @access private
#// 
#// @global string $required_php_version The required PHP version string.
#// @global string $wp_version           The WordPress version string.
#//
def wp_check_php_mysql_versions(*args_):
    
    global required_php_version,wp_version
    php_check_if_defined("required_php_version","wp_version")
    php_version = php_phpversion()
    if php_version_compare(required_php_version, php_version, ">"):
        protocol = wp_get_server_protocol()
        php_header(php_sprintf("%s 500 Internal Server Error", protocol), True, 500)
        php_header("Content-Type: text/html; charset=utf-8")
        printf("Your server is running PHP version %1$s but WordPress %2$s requires at least %3$s.", php_version, wp_version, required_php_version)
        php_print(1)
        php_exit()
    # end if
    if (not php_extension_loaded("mysql")) and (not php_extension_loaded("mysqli")) and (not php_extension_loaded("mysqlnd")) and (not php_file_exists(WP_CONTENT_DIR + "/db.php")):
        php_include_file(ABSPATH + WPINC + "/functions.php", once=True)
        wp_load_translations_early()
        args = Array({"exit": False, "code": "mysql_not_found"})
        wp_die(__("Your PHP installation appears to be missing the MySQL extension which is required by WordPress."), __("Requirements Not Met"), args)
        php_print(1)
        php_exit()
    # end if
# end def wp_check_php_mysql_versions
#// 
#// Don't load all of WordPress when handling a favicon.ico request.
#// 
#// Instead, send the headers for a zero-length favicon and bail.
#// 
#// @since 3.0.0
#// @deprecated 5.4.0 Deprecated in favor of do_favicon().
#//
def wp_favicon_request(*args_):
    
    if "/favicon.ico" == PHP_SERVER["REQUEST_URI"]:
        php_header("Content-Type: image/vnd.microsoft.icon")
        php_exit(0)
    # end if
# end def wp_favicon_request
#// 
#// Die with a maintenance message when conditions are met.
#// 
#// Checks for a file in the WordPress root directory named ".maintenance".
#// This file will contain the variable $upgrading, set to the time the file
#// was created. If the file was created less than 10 minutes ago, WordPress
#// enters maintenance mode and displays a message.
#// 
#// The default message can be replaced by using a drop-in (maintenance.php in
#// the wp-content directory).
#// 
#// @since 3.0.0
#// @access private
#// 
#// @global int $upgrading the unix timestamp marking when upgrading WordPress began.
#//
def wp_maintenance(*args_):
    
    if (not php_file_exists(ABSPATH + ".maintenance")) or wp_installing():
        return
    # end if
    global upgrading
    php_check_if_defined("upgrading")
    php_include_file(ABSPATH + ".maintenance", once=False)
    #// If the $upgrading timestamp is older than 10 minutes, don't die.
    if time() - upgrading >= 600:
        return
    # end if
    #// 
    #// Filters whether to enable maintenance mode.
    #// 
    #// This filter runs before it can be used by plugins. It is designed for
    #// non-web runtimes. If this filter returns true, maintenance mode will be
    #// active and the request will end. If false, the request will be allowed to
    #// continue processing even if maintenance mode should be active.
    #// 
    #// @since 4.6.0
    #// 
    #// @param bool $enable_checks Whether to enable maintenance mode. Default true.
    #// @param int  $upgrading     The timestamp set in the .maintenance file.
    #//
    if (not apply_filters("enable_maintenance_mode", True, upgrading)):
        return
    # end if
    if php_file_exists(WP_CONTENT_DIR + "/maintenance.php"):
        php_include_file(WP_CONTENT_DIR + "/maintenance.php", once=True)
        php_exit(0)
    # end if
    php_include_file(ABSPATH + WPINC + "/functions.php", once=True)
    wp_load_translations_early()
    php_header("Retry-After: 600")
    wp_die(__("Briefly unavailable for scheduled maintenance. Check back in a minute."), __("Maintenance"), 503)
# end def wp_maintenance
#// 
#// Start the WordPress micro-timer.
#// 
#// @since 0.71
#// @access private
#// 
#// @global float $timestart Unix timestamp set at the beginning of the page load.
#// @see timer_stop()
#// 
#// @return bool Always returns true.
#//
def timer_start(*args_):
    
    global timestart
    php_check_if_defined("timestart")
    timestart = php_microtime(True)
    return True
# end def timer_start
#// 
#// Retrieve or display the time from the page start to when function is called.
#// 
#// @since 0.71
#// 
#// @global float   $timestart Seconds from when timer_start() is called.
#// @global float   $timeend   Seconds from when function is called.
#// 
#// @param int|bool $display   Whether to echo or return the results. Accepts 0|false for return,
#// 1|true for echo. Default 0|false.
#// @param int      $precision The number of digits from the right of the decimal to display.
#// Default 3.
#// @return string The "second.microsecond" finished time calculation. The number is formatted
#// for human consumption, both localized and rounded.
#//
def timer_stop(display=0, precision=3, *args_):
    
    global timestart,timeend
    php_check_if_defined("timestart","timeend")
    timeend = php_microtime(True)
    timetotal = timeend - timestart
    r = number_format_i18n(timetotal, precision) if php_function_exists("number_format_i18n") else number_format(timetotal, precision)
    if display:
        php_print(r)
    # end if
    return r
# end def timer_stop
#// 
#// Set PHP error reporting based on WordPress debug settings.
#// 
#// Uses three constants: `WP_DEBUG`, `WP_DEBUG_DISPLAY`, and `WP_DEBUG_LOG`.
#// All three can be defined in wp-config.php. By default, `WP_DEBUG` and
#// `WP_DEBUG_LOG` are set to false, and `WP_DEBUG_DISPLAY` is set to true.
#// 
#// When `WP_DEBUG` is true, all PHP notices are reported. WordPress will also
#// display internal notices: when a deprecated WordPress function, function
#// argument, or file is used. Deprecated code may be removed from a later
#// version.
#// 
#// It is strongly recommended that plugin and theme developers use `WP_DEBUG`
#// in their development environments.
#// 
#// `WP_DEBUG_DISPLAY` and `WP_DEBUG_LOG` perform no function unless `WP_DEBUG`
#// is true.
#// 
#// When `WP_DEBUG_DISPLAY` is true, WordPress will force errors to be displayed.
#// `WP_DEBUG_DISPLAY` defaults to true. Defining it as null prevents WordPress
#// from changing the global configuration setting. Defining `WP_DEBUG_DISPLAY`
#// as false will force errors to be hidden.
#// 
#// When `WP_DEBUG_LOG` is true, errors will be logged to `wp-content/debug.log`.
#// When `WP_DEBUG_LOG` is a valid path, errors will be logged to the specified file.
#// 
#// Errors are never displayed for XML-RPC, REST, and Ajax requests.
#// 
#// @since 3.0.0
#// @since 5.1.0 `WP_DEBUG_LOG` can be a file path.
#// @access private
#//
def wp_debug_mode(*args_):
    
    #// 
    #// Filters whether to allow the debug mode check to occur.
    #// 
    #// This filter runs before it can be used by plugins. It is designed for
    #// non-web run-times. Returning false causes the `WP_DEBUG` and related
    #// constants to not be checked and the default PHP values for errors
    #// will be used unless you take care to update them yourself.
    #// 
    #// @since 4.6.0
    #// 
    #// @param bool $enable_debug_mode Whether to enable debug mode checks to occur. Default true.
    #//
    if (not apply_filters("enable_wp_debug_mode_checks", True)):
        return
    # end if
    if WP_DEBUG:
        php_error_reporting(E_ALL)
        if WP_DEBUG_DISPLAY:
            php_ini_set("display_errors", 1)
        elif None != WP_DEBUG_DISPLAY:
            php_ini_set("display_errors", 0)
        # end if
        if php_in_array(php_strtolower(str(WP_DEBUG_LOG)), Array("true", "1"), True):
            log_path = WP_CONTENT_DIR + "/debug.log"
        elif php_is_string(WP_DEBUG_LOG):
            log_path = WP_DEBUG_LOG
        else:
            log_path = False
        # end if
        if log_path:
            php_ini_set("log_errors", 1)
            php_ini_set("error_log", log_path)
        # end if
    else:
        php_error_reporting(E_CORE_ERROR | E_CORE_WARNING | E_COMPILE_ERROR | E_ERROR | E_WARNING | E_PARSE | E_USER_ERROR | E_USER_WARNING | E_RECOVERABLE_ERROR)
    # end if
    if php_defined("XMLRPC_REQUEST") or php_defined("REST_REQUEST") or php_defined("WP_INSTALLING") and WP_INSTALLING or wp_doing_ajax() or wp_is_json_request():
        php_ini_set("display_errors", 0)
    # end if
# end def wp_debug_mode
#// 
#// Set the location of the language directory.
#// 
#// To set directory manually, define the `WP_LANG_DIR` constant
#// in wp-config.php.
#// 
#// If the language directory exists within `WP_CONTENT_DIR`, it
#// is used. Otherwise the language directory is assumed to live
#// in `WPINC`.
#// 
#// @since 3.0.0
#// @access private
#//
def wp_set_lang_dir(*args_):
    
    if (not php_defined("WP_LANG_DIR")):
        if php_file_exists(WP_CONTENT_DIR + "/languages") and php_no_error(lambda: php_is_dir(WP_CONTENT_DIR + "/languages")) or (not php_no_error(lambda: php_is_dir(ABSPATH + WPINC + "/languages"))):
            #// 
            #// Server path of the language directory.
            #// 
            #// No leading slash, no trailing slash, full path, not relative to ABSPATH
            #// 
            #// @since 2.1.0
            #//
            php_define("WP_LANG_DIR", WP_CONTENT_DIR + "/languages")
            if (not php_defined("LANGDIR")):
                #// Old static relative path maintained for limited backward compatibility - won't work in some cases.
                php_define("LANGDIR", "wp-content/languages")
            # end if
        else:
            #// 
            #// Server path of the language directory.
            #// 
            #// No leading slash, no trailing slash, full path, not relative to `ABSPATH`.
            #// 
            #// @since 2.1.0
            #//
            php_define("WP_LANG_DIR", ABSPATH + WPINC + "/languages")
            if (not php_defined("LANGDIR")):
                #// Old relative path maintained for backward compatibility.
                php_define("LANGDIR", WPINC + "/languages")
            # end if
        # end if
    # end if
# end def wp_set_lang_dir
#// 
#// Load the database class file and instantiate the `$wpdb` global.
#// 
#// @since 2.5.0
#// 
#// @global wpdb $wpdb WordPress database abstraction object.
#//
def require_wp_db(*args_):
    
    global wpdb
    php_check_if_defined("wpdb")
    php_include_file(ABSPATH + WPINC + "/wp-db.php", once=True)
    if php_file_exists(WP_CONTENT_DIR + "/db.php"):
        php_include_file(WP_CONTENT_DIR + "/db.php", once=True)
    # end if
    if (php_isset(lambda : wpdb)):
        return
    # end if
    dbuser = DB_USER if php_defined("DB_USER") else ""
    dbpassword = DB_PASSWORD if php_defined("DB_PASSWORD") else ""
    dbname = DB_NAME if php_defined("DB_NAME") else ""
    dbhost = DB_HOST if php_defined("DB_HOST") else ""
    wpdb = php_new_class("wpdb", lambda : wpdb(dbuser, dbpassword, dbname, dbhost))
# end def require_wp_db
#// 
#// Set the database table prefix and the format specifiers for database
#// table columns.
#// 
#// Columns not listed here default to `%s`.
#// 
#// @since 3.0.0
#// @access private
#// 
#// @global wpdb   $wpdb         WordPress database abstraction object.
#// @global string $table_prefix The database table prefix.
#//
def wp_set_wpdb_vars(*args_):
    
    global wpdb,table_prefix
    php_check_if_defined("wpdb","table_prefix")
    if (not php_empty(lambda : wpdb.error)):
        dead_db()
    # end if
    wpdb.field_types = Array({"post_author": "%d", "post_parent": "%d", "menu_order": "%d", "term_id": "%d", "term_group": "%d", "term_taxonomy_id": "%d", "parent": "%d", "count": "%d", "object_id": "%d", "term_order": "%d", "ID": "%d", "comment_ID": "%d", "comment_post_ID": "%d", "comment_parent": "%d", "user_id": "%d", "link_id": "%d", "link_owner": "%d", "link_rating": "%d", "option_id": "%d", "blog_id": "%d", "meta_id": "%d", "post_id": "%d", "user_status": "%d", "umeta_id": "%d", "comment_karma": "%d", "comment_count": "%d", "active": "%d", "cat_id": "%d", "deleted": "%d", "lang_id": "%d", "mature": "%d", "public": "%d", "site_id": "%d", "spam": "%d"})
    prefix = wpdb.set_prefix(table_prefix)
    if is_wp_error(prefix):
        wp_load_translations_early()
        wp_die(php_sprintf(__("<strong>Error</strong>: %1$s in %2$s can only contain numbers, letters, and underscores."), "<code>$table_prefix</code>", "<code>wp-config.php</code>"))
    # end if
# end def wp_set_wpdb_vars
#// 
#// Toggle `$_wp_using_ext_object_cache` on and off without directly
#// touching global.
#// 
#// @since 3.7.0
#// 
#// @global bool $_wp_using_ext_object_cache
#// 
#// @param bool $using Whether external object cache is being used.
#// @return bool The current 'using' setting.
#//
def wp_using_ext_object_cache(using=None, *args_):
    
    global _wp_using_ext_object_cache
    php_check_if_defined("_wp_using_ext_object_cache")
    current_using = _wp_using_ext_object_cache
    if None != using:
        _wp_using_ext_object_cache = using
    # end if
    return current_using
# end def wp_using_ext_object_cache
#// 
#// Start the WordPress object cache.
#// 
#// If an object-cache.php file exists in the wp-content directory,
#// it uses that drop-in as an external object cache.
#// 
#// @since 3.0.0
#// @access private
#// 
#// @global array $wp_filter Stores all of the filters.
#//
def wp_start_object_cache(*args_):
    
    global wp_filter
    php_check_if_defined("wp_filter")
    first_init = True
    #// Only perform the following checks once.
    if first_init:
        if (not php_function_exists("wp_cache_init")):
            #// 
            #// This is the normal situation. First-run of this function. No
            #// caching backend has been loaded.
            #// 
            #// We try to load a custom caching backend, and then, if it
            #// results in a wp_cache_init() function existing, we note
            #// that an external object cache is being used.
            #//
            if php_file_exists(WP_CONTENT_DIR + "/object-cache.php"):
                php_include_file(WP_CONTENT_DIR + "/object-cache.php", once=True)
                if php_function_exists("wp_cache_init"):
                    wp_using_ext_object_cache(True)
                # end if
                #// Re-initialize any hooks added manually by object-cache.php.
                if wp_filter:
                    wp_filter = WP_Hook.build_preinitialized_hooks(wp_filter)
                # end if
            # end if
        elif (not wp_using_ext_object_cache()) and php_file_exists(WP_CONTENT_DIR + "/object-cache.php"):
            #// 
            #// Sometimes advanced-cache.php can load object-cache.php before
            #// this function is run. This breaks the function_exists() check
            #// above and can result in wp_using_ext_object_cache() returning
            #// false when actually an external cache is in use.
            #//
            wp_using_ext_object_cache(True)
        # end if
    # end if
    if (not wp_using_ext_object_cache()):
        php_include_file(ABSPATH + WPINC + "/cache.php", once=True)
    # end if
    #// 
    #// If cache supports reset, reset instead of init if already
    #// initialized. Reset signals to the cache that global IDs
    #// have changed and it may need to update keys and cleanup caches.
    #//
    if (not first_init) and php_function_exists("wp_cache_switch_to_blog"):
        wp_cache_switch_to_blog(get_current_blog_id())
    elif php_function_exists("wp_cache_init"):
        wp_cache_init()
    # end if
    if php_function_exists("wp_cache_add_global_groups"):
        wp_cache_add_global_groups(Array("users", "userlogins", "usermeta", "user_meta", "useremail", "userslugs", "site-transient", "site-options", "blog-lookup", "blog-details", "site-details", "rss", "global-posts", "blog-id-cache", "networks", "sites", "blog_meta"))
        wp_cache_add_non_persistent_groups(Array("counts", "plugins"))
    # end if
    first_init = False
# end def wp_start_object_cache
#// 
#// Redirect to the installer if WordPress is not installed.
#// 
#// Dies with an error message when Multisite is enabled.
#// 
#// @since 3.0.0
#// @access private
#//
def wp_not_installed(*args_):
    
    if is_multisite():
        if (not is_blog_installed()) and (not wp_installing()):
            nocache_headers()
            wp_die(__("The site you have requested is not installed properly. Please contact the system administrator."))
        # end if
    elif (not is_blog_installed()) and (not wp_installing()):
        nocache_headers()
        php_include_file(ABSPATH + WPINC + "/kses.php", once=False)
        php_include_file(ABSPATH + WPINC + "/pluggable.php", once=False)
        link = wp_guess_url() + "/wp-admin/install.php"
        wp_redirect(link)
        php_exit(0)
    # end if
# end def wp_not_installed
#// 
#// Retrieve an array of must-use plugin files.
#// 
#// The default directory is wp-content/mu-plugins. To change the default
#// directory manually, define `WPMU_PLUGIN_DIR` and `WPMU_PLUGIN_URL`
#// in wp-config.php.
#// 
#// @since 3.0.0
#// @access private
#// 
#// @return string[] Array of absolute paths of files to include.
#//
def wp_get_mu_plugins(*args_):
    
    mu_plugins = Array()
    if (not php_is_dir(WPMU_PLUGIN_DIR)):
        return mu_plugins
    # end if
    dh = php_opendir(WPMU_PLUGIN_DIR)
    if (not dh):
        return mu_plugins
    # end if
    while True:
        plugin = php_readdir(dh)
        if not (plugin != False):
            break
        # end if
        if php_substr(plugin, -4) == ".php":
            mu_plugins[-1] = WPMU_PLUGIN_DIR + "/" + plugin
        # end if
    # end while
    php_closedir(dh)
    sort(mu_plugins)
    return mu_plugins
# end def wp_get_mu_plugins
#// 
#// Retrieve an array of active and valid plugin files.
#// 
#// While upgrading or installing WordPress, no plugins are returned.
#// 
#// The default directory is `wp-content/plugins`. To change the default
#// directory manually, define `WP_PLUGIN_DIR` and `WP_PLUGIN_URL`
#// in `wp-config.php`.
#// 
#// @since 3.0.0
#// @access private
#// 
#// @return string[] $plugin_file Array of paths to plugin files relative to the plugins directory.
#//
def wp_get_active_and_valid_plugins(*args_):
    
    plugins = Array()
    active_plugins = get_option("active_plugins", Array())
    #// Check for hacks file if the option is enabled.
    if get_option("hack_file") and php_file_exists(ABSPATH + "my-hacks.php"):
        _deprecated_file("my-hacks.php", "1.5.0")
        array_unshift(plugins, ABSPATH + "my-hacks.php")
    # end if
    if php_empty(lambda : active_plugins) or wp_installing():
        return plugins
    # end if
    network_plugins = wp_get_active_network_plugins() if is_multisite() else False
    for plugin in active_plugins:
        if (not validate_file(plugin)) and ".php" == php_substr(plugin, -4) and php_file_exists(WP_PLUGIN_DIR + "/" + plugin) and (not network_plugins) or (not php_in_array(WP_PLUGIN_DIR + "/" + plugin, network_plugins)):
            plugins[-1] = WP_PLUGIN_DIR + "/" + plugin
        # end if
    # end for
    #// 
    #// Remove plugins from the list of active plugins when we're on an endpoint
    #// that should be protected against WSODs and the plugin is paused.
    #//
    if wp_is_recovery_mode():
        plugins = wp_skip_paused_plugins(plugins)
    # end if
    return plugins
# end def wp_get_active_and_valid_plugins
#// 
#// Filters a given list of plugins, removing any paused plugins from it.
#// 
#// @since 5.2.0
#// 
#// @param string[] $plugins Array of absolute plugin main file paths.
#// @return string[] Filtered array of plugins, without any paused plugins.
#//
def wp_skip_paused_plugins(plugins=None, *args_):
    global PHP_GLOBALS
    paused_plugins = wp_paused_plugins().get_all()
    if php_empty(lambda : paused_plugins):
        return plugins
    # end if
    for index,plugin in plugins:
        plugin = php_explode("/", plugin_basename(plugin))
        if php_array_key_exists(plugin, paused_plugins):
            plugins[index] = None
            #// Store list of paused plugins for displaying an admin notice.
            PHP_GLOBALS["_paused_plugins"][plugin] = paused_plugins[plugin]
        # end if
    # end for
    return plugins
# end def wp_skip_paused_plugins
#// 
#// Retrieves an array of active and valid themes.
#// 
#// While upgrading or installing WordPress, no themes are returned.
#// 
#// @since 5.1.0
#// @access private
#// 
#// @return string[] Array of absolute paths to theme directories.
#//
def wp_get_active_and_valid_themes(*args_):
    
    global pagenow
    php_check_if_defined("pagenow")
    themes = Array()
    if wp_installing() and "wp-activate.php" != pagenow:
        return themes
    # end if
    if TEMPLATEPATH != STYLESHEETPATH:
        themes[-1] = STYLESHEETPATH
    # end if
    themes[-1] = TEMPLATEPATH
    #// 
    #// Remove themes from the list of active themes when we're on an endpoint
    #// that should be protected against WSODs and the theme is paused.
    #//
    if wp_is_recovery_mode():
        themes = wp_skip_paused_themes(themes)
        #// If no active and valid themes exist, skip loading themes.
        if php_empty(lambda : themes):
            add_filter("wp_using_themes", "__return_false")
        # end if
    # end if
    return themes
# end def wp_get_active_and_valid_themes
#// 
#// Filters a given list of themes, removing any paused themes from it.
#// 
#// @since 5.2.0
#// 
#// @param string[] $themes Array of absolute theme directory paths.
#// @return string[] Filtered array of absolute paths to themes, without any paused themes.
#//
def wp_skip_paused_themes(themes=None, *args_):
    global PHP_GLOBALS
    paused_themes = wp_paused_themes().get_all()
    if php_empty(lambda : paused_themes):
        return themes
    # end if
    for index,theme in themes:
        theme = php_basename(theme)
        if php_array_key_exists(theme, paused_themes):
            themes[index] = None
            #// Store list of paused themes for displaying an admin notice.
            PHP_GLOBALS["_paused_themes"][theme] = paused_themes[theme]
        # end if
    # end for
    return themes
# end def wp_skip_paused_themes
#// 
#// Is WordPress in Recovery Mode.
#// 
#// In this mode, plugins or themes that cause WSODs will be paused.
#// 
#// @since 5.2.0
#// 
#// @return bool
#//
def wp_is_recovery_mode(*args_):
    
    return wp_recovery_mode().is_active()
# end def wp_is_recovery_mode
#// 
#// Determines whether we are currently on an endpoint that should be protected against WSODs.
#// 
#// @since 5.2.0
#// 
#// @return bool True if the current endpoint should be protected.
#//
def is_protected_endpoint(*args_):
    
    #// Protect login pages.
    if (php_isset(lambda : PHP_GLOBALS["pagenow"])) and "wp-login.php" == PHP_GLOBALS["pagenow"]:
        return True
    # end if
    #// Protect the admin backend.
    if is_admin() and (not wp_doing_ajax()):
        return True
    # end if
    #// Protect AJAX actions that could help resolve a fatal error should be available.
    if is_protected_ajax_action():
        return True
    # end if
    #// 
    #// Filters whether the current request is against a protected endpoint.
    #// 
    #// This filter is only fired when an endpoint is requested which is not already protected by
    #// WordPress core. As such, it exclusively allows providing further protected endpoints in
    #// addition to the admin backend, login pages and protected AJAX actions.
    #// 
    #// @since 5.2.0
    #// 
    #// @param bool $is_protected_endpoint Whether the currently requested endpoint is protected. Default false.
    #//
    return bool(apply_filters("is_protected_endpoint", False))
# end def is_protected_endpoint
#// 
#// Determines whether we are currently handling an AJAX action that should be protected against WSODs.
#// 
#// @since 5.2.0
#// 
#// @return bool True if the current AJAX action should be protected.
#//
def is_protected_ajax_action(*args_):
    
    if (not wp_doing_ajax()):
        return False
    # end if
    if (not (php_isset(lambda : PHP_REQUEST["action"]))):
        return False
    # end if
    actions_to_protect = Array("edit-theme-plugin-file", "heartbeat", "install-plugin", "install-theme", "search-plugins", "search-install-plugins", "update-plugin", "update-theme")
    #// 
    #// Filters the array of protected AJAX actions.
    #// 
    #// This filter is only fired when doing AJAX and the AJAX request has an 'action' property.
    #// 
    #// @since 5.2.0
    #// 
    #// @param string[] $actions_to_protect Array of strings with AJAX actions to protect.
    #//
    actions_to_protect = apply_filters("wp_protected_ajax_actions", actions_to_protect)
    if (not php_in_array(PHP_REQUEST["action"], actions_to_protect, True)):
        return False
    # end if
    return True
# end def is_protected_ajax_action
#// 
#// Set internal encoding.
#// 
#// In most cases the default internal encoding is latin1, which is
#// of no use, since we want to use the `mb_` functions for `utf-8` strings.
#// 
#// @since 3.0.0
#// @access private
#//
def wp_set_internal_encoding(*args_):
    
    if php_function_exists("mb_internal_encoding"):
        charset = get_option("blog_charset")
        #// phpcs:ignore WordPress.PHP.NoSilencedErrors.Discouraged
        if (not charset) or (not php_no_error(lambda: mb_internal_encoding(charset))):
            mb_internal_encoding("UTF-8")
        # end if
    # end if
# end def wp_set_internal_encoding
#// 
#// Add magic quotes to `$_GET`, `$_POST`, `$_COOKIE`, and `$_SERVER`.
#// 
#// Also forces `$_REQUEST` to be `$_GET + $_POST`. If `$_SERVER`,
#// `$_COOKIE`, or `$_ENV` are needed, use those superglobals directly.
#// 
#// @since 3.0.0
#// @access private
#//
def wp_magic_quotes(*args_):
    global PHP_REQUEST, PHP_POST, PHP_COOKIE, PHP_SERVER
    #// Escape with wpdb.
    PHP_REQUEST = add_magic_quotes(PHP_REQUEST)
    PHP_POST = add_magic_quotes(PHP_POST)
    PHP_COOKIE = add_magic_quotes(PHP_COOKIE)
    PHP_SERVER = add_magic_quotes(PHP_SERVER)
    #// 
    #// Revert the type change to string for two indexes which should retain their proper type.
    #// Among other things, this preserves compatibility of WP with PHPUnit Code Coverage generation.
    #//
    if (php_isset(lambda : PHP_SERVER["REQUEST_TIME"])):
        PHP_SERVER["REQUEST_TIME"] = int(PHP_SERVER["REQUEST_TIME"])
    # end if
    if (php_isset(lambda : PHP_SERVER["REQUEST_TIME_FLOAT"])):
        PHP_SERVER["REQUEST_TIME_FLOAT"] = float(PHP_SERVER["REQUEST_TIME_FLOAT"])
    # end if
    #// Force REQUEST to be GET + POST.
    PHP_REQUEST = php_array_merge(PHP_REQUEST, PHP_POST)
# end def wp_magic_quotes
#// 
#// Runs just before PHP shuts down execution.
#// 
#// @since 1.2.0
#// @access private
#//
def shutdown_action_hook(*args_):
    
    #// 
    #// Fires just before PHP shuts down execution.
    #// 
    #// @since 1.2.0
    #//
    do_action("shutdown")
    wp_cache_close()
# end def shutdown_action_hook
#// 
#// Copy an object.
#// 
#// @since 2.7.0
#// @deprecated 3.2.0
#// 
#// @param object $object The object to clone.
#// @return object The cloned object.
#//
def wp_clone(object=None, *args_):
    
    #// Use parens for clone to accommodate PHP 4. See #17880.
    return copy.deepcopy(object)
# end def wp_clone
#// 
#// Determines whether the current request is for an administrative interface page.
#// 
#// Does not check if the user is an administrator; use current_user_can()
#// for checking roles and capabilities.
#// 
#// For more information on this and similar theme functions, check out
#// the {@link https://developer.wordpress.org/themes/basics/conditional-tags
#// Conditional Tags} article in the Theme Developer Handbook.
#// 
#// @since 1.5.1
#// 
#// @global WP_Screen $current_screen WordPress current screen object.
#// 
#// @return bool True if inside WordPress administration interface, false otherwise.
#//
def is_admin(*args_):
    
    if (php_isset(lambda : PHP_GLOBALS["current_screen"])):
        return PHP_GLOBALS["current_screen"].in_admin()
    elif php_defined("WP_ADMIN"):
        return WP_ADMIN
    # end if
    return False
# end def is_admin
#// 
#// Whether the current request is for a site's administrative interface.
#// 
#// e.g. `/wp-admin/`
#// 
#// Does not check if the user is an administrator; use current_user_can()
#// for checking roles and capabilities.
#// 
#// @since 3.1.0
#// 
#// @global WP_Screen $current_screen WordPress current screen object.
#// 
#// @return bool True if inside WordPress blog administration pages.
#//
def is_blog_admin(*args_):
    
    if (php_isset(lambda : PHP_GLOBALS["current_screen"])):
        return PHP_GLOBALS["current_screen"].in_admin("site")
    elif php_defined("WP_BLOG_ADMIN"):
        return WP_BLOG_ADMIN
    # end if
    return False
# end def is_blog_admin
#// 
#// Whether the current request is for the network administrative interface.
#// 
#// e.g. `/wp-admin/network/`
#// 
#// Does not check if the user is an administrator; use current_user_can()
#// for checking roles and capabilities.
#// 
#// Does not check if the site is a Multisite network; use is_multisite()
#// for checking if Multisite is enabled.
#// 
#// @since 3.1.0
#// 
#// @global WP_Screen $current_screen WordPress current screen object.
#// 
#// @return bool True if inside WordPress network administration pages.
#//
def is_network_admin(*args_):
    
    if (php_isset(lambda : PHP_GLOBALS["current_screen"])):
        return PHP_GLOBALS["current_screen"].in_admin("network")
    elif php_defined("WP_NETWORK_ADMIN"):
        return WP_NETWORK_ADMIN
    # end if
    return False
# end def is_network_admin
#// 
#// Whether the current request is for a user admin screen.
#// 
#// e.g. `/wp-admin/user/`
#// 
#// Does not check if the user is an administrator; use current_user_can()
#// for checking roles and capabilities.
#// 
#// @since 3.1.0
#// 
#// @global WP_Screen $current_screen WordPress current screen object.
#// 
#// @return bool True if inside WordPress user administration pages.
#//
def is_user_admin(*args_):
    
    if (php_isset(lambda : PHP_GLOBALS["current_screen"])):
        return PHP_GLOBALS["current_screen"].in_admin("user")
    elif php_defined("WP_USER_ADMIN"):
        return WP_USER_ADMIN
    # end if
    return False
# end def is_user_admin
#// 
#// If Multisite is enabled.
#// 
#// @since 3.0.0
#// 
#// @return bool True if Multisite is enabled, false otherwise.
#//
def is_multisite(*args_):
    
    if php_defined("MULTISITE"):
        return MULTISITE
    # end if
    if php_defined("SUBDOMAIN_INSTALL") or php_defined("VHOST") or php_defined("SUNRISE"):
        return True
    # end if
    return False
# end def is_multisite
#// 
#// Retrieve the current site ID.
#// 
#// @since 3.1.0
#// 
#// @global int $blog_id
#// 
#// @return int Site ID.
#//
def get_current_blog_id(*args_):
    
    global blog_id
    php_check_if_defined("blog_id")
    return absint(blog_id)
# end def get_current_blog_id
#// 
#// Retrieves the current network ID.
#// 
#// @since 4.6.0
#// 
#// @return int The ID of the current network.
#//
def get_current_network_id(*args_):
    
    if (not is_multisite()):
        return 1
    # end if
    current_network = get_network()
    if (not (php_isset(lambda : current_network.id))):
        return get_main_network_id()
    # end if
    return absint(current_network.id)
# end def get_current_network_id
#// 
#// Attempt an early load of translations.
#// 
#// Used for errors encountered during the initial loading process, before
#// the locale has been properly detected and loaded.
#// 
#// Designed for unusual load sequences (like setup-config.php) or for when
#// the script will then terminate with an error, otherwise there is a risk
#// that a file can be double-included.
#// 
#// @since 3.4.0
#// @access private
#// 
#// @global WP_Locale $wp_locale WordPress date and time locale object.
#// 
#// @staticvar bool $loaded
#//
def wp_load_translations_early(*args_):
    
    global wp_locale
    php_check_if_defined("wp_locale")
    loaded = False
    if loaded:
        return
    # end if
    loaded = True
    if php_function_exists("did_action") and did_action("init"):
        return
    # end if
    #// We need $wp_local_package.
    php_include_file(ABSPATH + WPINC + "/version.php", once=False)
    #// Translation and localization.
    php_include_file(ABSPATH + WPINC + "/pomo/mo.php", once=True)
    php_include_file(ABSPATH + WPINC + "/l10n.php", once=True)
    php_include_file(ABSPATH + WPINC + "/class-wp-locale.php", once=True)
    php_include_file(ABSPATH + WPINC + "/class-wp-locale-switcher.php", once=True)
    #// General libraries.
    php_include_file(ABSPATH + WPINC + "/plugin.php", once=True)
    locales = Array()
    locations = Array()
    while True:
        
        if not (True):
            break
        # end if
        if php_defined("WPLANG"):
            if "" == WPLANG:
                break
            # end if
            locales[-1] = WPLANG
        # end if
        if (php_isset(lambda : wp_local_package)):
            locales[-1] = wp_local_package
        # end if
        if (not locales):
            break
        # end if
        if php_defined("WP_LANG_DIR") and php_no_error(lambda: php_is_dir(WP_LANG_DIR)):
            locations[-1] = WP_LANG_DIR
        # end if
        if php_defined("WP_CONTENT_DIR") and php_no_error(lambda: php_is_dir(WP_CONTENT_DIR + "/languages")):
            locations[-1] = WP_CONTENT_DIR + "/languages"
        # end if
        if php_no_error(lambda: php_is_dir(ABSPATH + "wp-content/languages")):
            locations[-1] = ABSPATH + "wp-content/languages"
        # end if
        if php_no_error(lambda: php_is_dir(ABSPATH + WPINC + "/languages")):
            locations[-1] = ABSPATH + WPINC + "/languages"
        # end if
        if (not locations):
            break
        # end if
        locations = array_unique(locations)
        for locale in locales:
            for location in locations:
                if php_file_exists(location + "/" + locale + ".mo"):
                    load_textdomain("default", location + "/" + locale + ".mo")
                    if php_defined("WP_SETUP_CONFIG") and php_file_exists(location + "/admin-" + locale + ".mo"):
                        load_textdomain("default", location + "/admin-" + locale + ".mo")
                    # end if
                    break
                # end if
            # end for
        # end for
        break
    # end while
    wp_locale = php_new_class("WP_Locale", lambda : WP_Locale())
# end def wp_load_translations_early
#// 
#// Check or set whether WordPress is in "installation" mode.
#// 
#// If the `WP_INSTALLING` constant is defined during the bootstrap, `wp_installing()` will default to `true`.
#// 
#// @since 4.4.0
#// 
#// @staticvar bool $installing
#// 
#// @param bool $is_installing Optional. True to set WP into Installing mode, false to turn Installing mode off.
#// Omit this parameter if you only want to fetch the current status.
#// @return bool True if WP is installing, otherwise false. When a `$is_installing` is passed, the function will
#// report whether WP was in installing mode prior to the change to `$is_installing`.
#//
def wp_installing(is_installing=None, *args_):
    
    installing = None
    #// Support for the `WP_INSTALLING` constant, defined before WP is loaded.
    if php_is_null(installing):
        installing = php_defined("WP_INSTALLING") and WP_INSTALLING
    # end if
    if (not php_is_null(is_installing)):
        old_installing = installing
        installing = is_installing
        return bool(old_installing)
    # end if
    return bool(installing)
# end def wp_installing
#// 
#// Determines if SSL is used.
#// 
#// @since 2.6.0
#// @since 4.6.0 Moved from functions.php to load.php.
#// 
#// @return bool True if SSL, otherwise false.
#//
def is_ssl(*args_):
    
    if (php_isset(lambda : PHP_SERVER["HTTPS"])):
        if "on" == php_strtolower(PHP_SERVER["HTTPS"]):
            return True
        # end if
        if "1" == PHP_SERVER["HTTPS"]:
            return True
        # end if
    elif (php_isset(lambda : PHP_SERVER["SERVER_PORT"])) and "443" == PHP_SERVER["SERVER_PORT"]:
        return True
    # end if
    return False
# end def is_ssl
#// 
#// Converts a shorthand byte value to an integer byte value.
#// 
#// @since 2.3.0
#// @since 4.6.0 Moved from media.php to load.php.
#// 
#// @link https://www.php.net/manual/en/function.ini-get.php
#// @link https://www.php.net/manual/en/faq.using.php#faq.using.shorthandbytes
#// 
#// @param string $value A (PHP ini) byte value, either shorthand or ordinary.
#// @return int An integer byte value.
#//
def wp_convert_hr_to_bytes(value=None, *args_):
    
    value = php_strtolower(php_trim(value))
    bytes = int(value)
    if False != php_strpos(value, "g"):
        bytes *= GB_IN_BYTES
    elif False != php_strpos(value, "m"):
        bytes *= MB_IN_BYTES
    elif False != php_strpos(value, "k"):
        bytes *= KB_IN_BYTES
    # end if
    #// Deal with large (float) values which run into the maximum integer size.
    return php_min(bytes, PHP_INT_MAX)
# end def wp_convert_hr_to_bytes
#// 
#// Determines whether a PHP ini value is changeable at runtime.
#// 
#// @since 4.6.0
#// 
#// @staticvar array $ini_all
#// 
#// @link https://www.php.net/manual/en/function.ini-get-all.php
#// 
#// @param string $setting The name of the ini setting to check.
#// @return bool True if the value is changeable at runtime. False otherwise.
#//
def wp_is_ini_value_changeable(setting=None, *args_):
    
    ini_all = None
    if (not (php_isset(lambda : ini_all))):
        ini_all = False
        #// Sometimes `ini_get_all()` is disabled via the `disable_functions` option for "security purposes".
        if php_function_exists("ini_get_all"):
            ini_all = php_ini_get_all()
        # end if
    # end if
    #// Bit operator to workaround https://bugs.php.net/bug.php?id=44936 which changes access level to 63 in PHP 5.2.6 - 5.2.17.
    if (php_isset(lambda : ini_all[setting]["access"])) and INI_ALL == ini_all[setting]["access"] & 7 or INI_USER == ini_all[setting]["access"] & 7:
        return True
    # end if
    #// If we were unable to retrieve the details, fail gracefully to assume it's changeable.
    if (not php_is_array(ini_all)):
        return True
    # end if
    return False
# end def wp_is_ini_value_changeable
#// 
#// Determines whether the current request is a WordPress Ajax request.
#// 
#// @since 4.7.0
#// 
#// @return bool True if it's a WordPress Ajax request, false otherwise.
#//
def wp_doing_ajax(*args_):
    
    #// 
    #// Filters whether the current request is a WordPress Ajax request.
    #// 
    #// @since 4.7.0
    #// 
    #// @param bool $wp_doing_ajax Whether the current request is a WordPress Ajax request.
    #//
    return apply_filters("wp_doing_ajax", php_defined("DOING_AJAX") and DOING_AJAX)
# end def wp_doing_ajax
#// 
#// Determines whether the current request should use themes.
#// 
#// @since 5.1.0
#// 
#// @return bool True if themes should be used, false otherwise.
#//
def wp_using_themes(*args_):
    
    #// 
    #// Filters whether the current request should use themes.
    #// 
    #// @since 5.1.0
    #// 
    #// @param bool $wp_using_themes Whether the current request should use themes.
    #//
    return apply_filters("wp_using_themes", php_defined("WP_USE_THEMES") and WP_USE_THEMES)
# end def wp_using_themes
#// 
#// Determines whether the current request is a WordPress cron request.
#// 
#// @since 4.8.0
#// 
#// @return bool True if it's a WordPress cron request, false otherwise.
#//
def wp_doing_cron(*args_):
    
    #// 
    #// Filters whether the current request is a WordPress cron request.
    #// 
    #// @since 4.8.0
    #// 
    #// @param bool $wp_doing_cron Whether the current request is a WordPress cron request.
    #//
    return apply_filters("wp_doing_cron", php_defined("DOING_CRON") and DOING_CRON)
# end def wp_doing_cron
#// 
#// Check whether variable is a WordPress Error.
#// 
#// Returns true if $thing is an object of the WP_Error class.
#// 
#// @since 2.1.0
#// 
#// @param mixed $thing Check if unknown variable is a WP_Error object.
#// @return bool True, if WP_Error. False, if not WP_Error.
#//
def is_wp_error(thing=None, *args_):
    
    return type(thing).__name__ == "WP_Error"
# end def is_wp_error
#// 
#// Determines whether file modifications are allowed.
#// 
#// @since 4.8.0
#// 
#// @param string $context The usage context.
#// @return bool True if file modification is allowed, false otherwise.
#//
def wp_is_file_mod_allowed(context=None, *args_):
    
    #// 
    #// Filters whether file modifications are allowed.
    #// 
    #// @since 4.8.0
    #// 
    #// @param bool   $file_mod_allowed Whether file modifications are allowed.
    #// @param string $context          The usage context.
    #//
    return apply_filters("file_mod_allowed", (not php_defined("DISALLOW_FILE_MODS")) or (not DISALLOW_FILE_MODS), context)
# end def wp_is_file_mod_allowed
#// 
#// Start scraping edited file errors.
#// 
#// @since 4.9.0
#//
def wp_start_scraping_edited_file_errors(*args_):
    
    if (not (php_isset(lambda : PHP_REQUEST["wp_scrape_key"]))) or (not (php_isset(lambda : PHP_REQUEST["wp_scrape_nonce"]))):
        return
    # end if
    key = php_substr(sanitize_key(wp_unslash(PHP_REQUEST["wp_scrape_key"])), 0, 32)
    nonce = wp_unslash(PHP_REQUEST["wp_scrape_nonce"])
    if get_transient("scrape_key_" + key) != nonce:
        php_print(str("###### wp_scraping_result_start:") + str(key) + str(" ######"))
        php_print(wp_json_encode(Array({"code": "scrape_nonce_failure", "message": __("Scrape nonce check failed. Please try again.")})))
        php_print(str("###### wp_scraping_result_end:") + str(key) + str(" ######"))
        php_exit(0)
    # end if
    if (not php_defined("WP_SANDBOX_SCRAPING")):
        php_define("WP_SANDBOX_SCRAPING", True)
    # end if
    php_register_shutdown_function("wp_finalize_scraping_edited_file_errors", key)
# end def wp_start_scraping_edited_file_errors
#// 
#// Finalize scraping for edited file errors.
#// 
#// @since 4.9.0
#// 
#// @param string $scrape_key Scrape key.
#//
def wp_finalize_scraping_edited_file_errors(scrape_key=None, *args_):
    
    error = error_get_last()
    php_print(str("\n###### wp_scraping_result_start:") + str(scrape_key) + str(" ######\n"))
    if (not php_empty(lambda : error)) and php_in_array(error["type"], Array(E_CORE_ERROR, E_COMPILE_ERROR, E_ERROR, E_PARSE, E_USER_ERROR, E_RECOVERABLE_ERROR), True):
        error = php_str_replace(ABSPATH, "", error)
        php_print(wp_json_encode(error))
    else:
        php_print(wp_json_encode(True))
    # end if
    php_print(str("\n###### wp_scraping_result_end:") + str(scrape_key) + str(" ######\n"))
# end def wp_finalize_scraping_edited_file_errors
#// 
#// Checks whether current request is a JSON request, or is expecting a JSON response.
#// 
#// @since 5.0.0
#// 
#// @return bool True if `Accepts` or `Content-Type` headers contain `application/json`.
#// False otherwise.
#//
def wp_is_json_request(*args_):
    
    if (php_isset(lambda : PHP_SERVER["HTTP_ACCEPT"])) and False != php_strpos(PHP_SERVER["HTTP_ACCEPT"], "application/json"):
        return True
    # end if
    if (php_isset(lambda : PHP_SERVER["CONTENT_TYPE"])) and "application/json" == PHP_SERVER["CONTENT_TYPE"]:
        return True
    # end if
    return False
# end def wp_is_json_request
#// 
#// Checks whether current request is a JSONP request, or is expecting a JSONP response.
#// 
#// @since 5.2.0
#// 
#// @return bool True if JSONP request, false otherwise.
#//
def wp_is_jsonp_request(*args_):
    
    if (not (php_isset(lambda : PHP_REQUEST["_jsonp"]))):
        return False
    # end if
    if (not php_function_exists("wp_check_jsonp_callback")):
        php_include_file(ABSPATH + WPINC + "/functions.php", once=True)
    # end if
    jsonp_callback = PHP_REQUEST["_jsonp"]
    if (not wp_check_jsonp_callback(jsonp_callback)):
        return False
    # end if
    #// This filter is documented in wp-includes/rest-api/class-wp-rest-server.php
    jsonp_enabled = apply_filters("rest_jsonp_enabled", True)
    return jsonp_enabled
# end def wp_is_jsonp_request
#// 
#// Checks whether current request is an XML request, or is expecting an XML response.
#// 
#// @since 5.2.0
#// 
#// @return bool True if `Accepts` or `Content-Type` headers contain `text/xml`
#// or one of the related MIME types. False otherwise.
#//
def wp_is_xml_request(*args_):
    
    accepted = Array("text/xml", "application/rss+xml", "application/atom+xml", "application/rdf+xml", "text/xml+oembed", "application/xml+oembed")
    if (php_isset(lambda : PHP_SERVER["HTTP_ACCEPT"])):
        for type in accepted:
            if False != php_strpos(PHP_SERVER["HTTP_ACCEPT"], type):
                return True
            # end if
        # end for
    # end if
    if (php_isset(lambda : PHP_SERVER["CONTENT_TYPE"])) and php_in_array(PHP_SERVER["CONTENT_TYPE"], accepted, True):
        return True
    # end if
    return False
# end def wp_is_xml_request