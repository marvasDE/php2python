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
#// New Post Administration Screen.
#// 
#// @package WordPress
#// @subpackage Administration
#// 
#// Load WordPress Administration Bootstrap
php_include_file(__DIR__ + "/admin.php", once=True)
#// 
#// @global string  $post_type
#// @global object  $post_type_object
#// @global WP_Post $post             Global post object.
#//
global post_type,post_type_object,post
php_check_if_defined("post_type","post_type_object","post")
if (not (php_isset(lambda : PHP_REQUEST["post_type"]))):
    post_type = "post"
elif php_in_array(PHP_REQUEST["post_type"], get_post_types(Array({"show_ui": True}))):
    post_type = PHP_REQUEST["post_type"]
else:
    wp_die(__("Invalid post type."))
# end if
post_type_object = get_post_type_object(post_type)
if "post" == post_type:
    parent_file = "edit.php"
    submenu_file = "post-new.php"
elif "attachment" == post_type:
    if wp_redirect(admin_url("media-new.php")):
        php_exit(0)
    # end if
else:
    submenu_file = str("post-new.php?post_type=") + str(post_type)
    if (php_isset(lambda : post_type_object)) and post_type_object.show_in_menu and True != post_type_object.show_in_menu:
        parent_file = post_type_object.show_in_menu
        #// What if there isn't a post-new.php item for this post type?
        if (not (php_isset(lambda : _registered_pages[get_plugin_page_hookname(str("post-new.php?post_type=") + str(post_type), post_type_object.show_in_menu)]))):
            if (php_isset(lambda : _registered_pages[get_plugin_page_hookname(str("edit.php?post_type=") + str(post_type), post_type_object.show_in_menu)])):
                #// Fall back to edit.php for that post type, if it exists.
                submenu_file = str("edit.php?post_type=") + str(post_type)
            else:
                #// Otherwise, give up and highlight the parent.
                submenu_file = parent_file
            # end if
        # end if
    else:
        parent_file = str("edit.php?post_type=") + str(post_type)
    # end if
# end if
title = post_type_object.labels.add_new_item
editing = True
if (not current_user_can(post_type_object.cap.edit_posts)) or (not current_user_can(post_type_object.cap.create_posts)):
    wp_die("<h1>" + __("You need a higher level of permission.") + "</h1>" + "<p>" + __("Sorry, you are not allowed to create posts as this user.") + "</p>", 403)
# end if
post = get_default_post_to_edit(post_type, True)
post_ID = post.ID
#// This filter is documented in wp-admin/post.php
if apply_filters("replace_editor", False, post) != True:
    if use_block_editor_for_post(post):
        php_include_file(ABSPATH + "wp-admin/edit-form-blocks.php", once=False)
    else:
        wp_enqueue_script("autosave")
        php_include_file(ABSPATH + "wp-admin/edit-form-advanced.php", once=False)
    # end if
else:
    #// Flag that we're not loading the block editor.
    current_screen = get_current_screen()
    current_screen.is_block_editor(False)
# end if
php_include_file(ABSPATH + "wp-admin/admin-footer.php", once=True)