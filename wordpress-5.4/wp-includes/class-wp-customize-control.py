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
#// WordPress Customize Control classes
#// 
#// @package WordPress
#// @subpackage Customize
#// @since 3.4.0
#// 
#// 
#// Customize Control class.
#// 
#// @since 3.4.0
#//
class WP_Customize_Control():
    instance_count = 0
    instance_number = Array()
    manager = Array()
    id = Array()
    settings = Array()
    setting = "default"
    capability = Array()
    priority = 10
    section = ""
    label = ""
    description = ""
    choices = Array()
    input_attrs = Array()
    allow_addition = False
    json = Array()
    type = "text"
    active_callback = ""
    #// 
    #// Constructor.
    #// 
    #// Supplied `$args` override class property defaults.
    #// 
    #// If `$args['settings']` is not defined, use the $id as the setting ID.
    #// 
    #// @since 3.4.0
    #// 
    #// @param WP_Customize_Manager $manager Customizer bootstrap instance.
    #// @param string               $id      Control ID.
    #// @param array                $args    {
    #// Optional. Array of properties for the new Control object. Default empty array.
    #// 
    #// @type int                  $instance_number Order in which this instance was created in relation
    #// to other instances.
    #// @type WP_Customize_Manager $manager         Customizer bootstrap instance.
    #// @type string               $id              Control ID.
    #// @type array                $settings        All settings tied to the control. If undefined, `$id` will
    #// be used.
    #// @type string               $setting         The primary setting for the control (if there is one).
    #// Default 'default'.
    #// @type string               $capability      Capability required to use this control. Normally this is empty
    #// and the capability is derived from `$settings`.
    #// @type int                  $priority        Order priority to load the control. Default 10.
    #// @type string               $section         Section the control belongs to. Default empty.
    #// @type string               $label           Label for the control. Default empty.
    #// @type string               $description     Description for the control. Default empty.
    #// @type array                $choices         List of choices for 'radio' or 'select' type controls, where
    #// values are the keys, and labels are the values.
    #// Default empty array.
    #// @type array                $input_attrs     List of custom input attributes for control output, where
    #// attribute names are the keys and values are the values. Not
    #// used for 'checkbox', 'radio', 'select', 'textarea', or
    #// 'dropdown-pages' control types. Default empty array.
    #// @type bool                 $allow_addition  Show UI for adding new content, currently only used for the
    #// dropdown-pages control. Default false.
    #// @type array                $json            Deprecated. Use WP_Customize_Control::json() instead.
    #// @type string               $type            Control type. Core controls include 'text', 'checkbox',
    #// 'textarea', 'radio', 'select', and 'dropdown-pages'. Additional
    #// input types such as 'email', 'url', 'number', 'hidden', and
    #// 'date' are supported implicitly. Default 'text'.
    #// @type callback             $active_callback Active callback.
    #// }
    #//
    def __init__(self, manager=None, id=None, args=Array()):
        
        keys = php_array_keys(get_object_vars(self))
        for key in keys:
            if (php_isset(lambda : args[key])):
                self.key = args[key]
            # end if
        # end for
        self.manager = manager
        self.id = id
        if php_empty(lambda : self.active_callback):
            self.active_callback = Array(self, "active_callback")
        # end if
        self.instance_count += 1
        self.instance_number = self.instance_count
        #// Process settings.
        if (not (php_isset(lambda : self.settings))):
            self.settings = id
        # end if
        settings = Array()
        if php_is_array(self.settings):
            for key,setting in self.settings:
                settings[key] = self.manager.get_setting(setting)
            # end for
        elif php_is_string(self.settings):
            self.setting = self.manager.get_setting(self.settings)
            settings["default"] = self.setting
        # end if
        self.settings = settings
    # end def __init__
    #// 
    #// Enqueue control related scripts/styles.
    #// 
    #// @since 3.4.0
    #//
    def enqueue(self):
        
        pass
    # end def enqueue
    #// 
    #// Check whether control is active to current Customizer preview.
    #// 
    #// @since 4.0.0
    #// 
    #// @return bool Whether the control is active to the current preview.
    #//
    def active(self):
        
        control = self
        active = php_call_user_func(self.active_callback, self)
        #// 
        #// Filters response of WP_Customize_Control::active().
        #// 
        #// @since 4.0.0
        #// 
        #// @param bool                 $active  Whether the Customizer control is active.
        #// @param WP_Customize_Control $control WP_Customize_Control instance.
        #//
        active = apply_filters("customize_control_active", active, control)
        return active
    # end def active
    #// 
    #// Default callback used when invoking WP_Customize_Control::active().
    #// 
    #// Subclasses can override this with their specific logic, or they may
    #// provide an 'active_callback' argument to the constructor.
    #// 
    #// @since 4.0.0
    #// 
    #// @return true Always true.
    #//
    def active_callback(self):
        
        return True
    # end def active_callback
    #// 
    #// Fetch a setting's value.
    #// Grabs the main setting by default.
    #// 
    #// @since 3.4.0
    #// 
    #// @param string $setting_key
    #// @return mixed The requested setting's value, if the setting exists.
    #//
    def value(self, setting_key="default"):
        
        if (php_isset(lambda : self.settings[setting_key])):
            return self.settings[setting_key].value()
        # end if
    # end def value
    #// 
    #// Refresh the parameters passed to the JavaScript via JSON.
    #// 
    #// @since 3.4.0
    #//
    def to_json(self):
        
        self.json["settings"] = Array()
        for key,setting in self.settings:
            self.json["settings"][key] = setting.id
        # end for
        self.json["type"] = self.type
        self.json["priority"] = self.priority
        self.json["active"] = self.active()
        self.json["section"] = self.section
        self.json["content"] = self.get_content()
        self.json["label"] = self.label
        self.json["description"] = self.description
        self.json["instanceNumber"] = self.instance_number
        if "dropdown-pages" == self.type:
            self.json["allow_addition"] = self.allow_addition
        # end if
    # end def to_json
    #// 
    #// Get the data to export to the client via JSON.
    #// 
    #// @since 4.1.0
    #// 
    #// @return array Array of parameters passed to the JavaScript.
    #//
    def json(self):
        
        self.to_json()
        return self.json
    # end def json
    #// 
    #// Checks if the user can use this control.
    #// 
    #// Returns false if the user cannot manipulate one of the associated settings,
    #// or if one of the associated settings does not exist. Also returns false if
    #// the associated section does not exist or if its capability check returns
    #// false.
    #// 
    #// @since 3.4.0
    #// 
    #// @return bool False if theme doesn't support the control or user doesn't have the required permissions, otherwise true.
    #//
    def check_capabilities(self):
        
        if (not php_empty(lambda : self.capability)) and (not current_user_can(self.capability)):
            return False
        # end if
        for setting in self.settings:
            if (not setting) or (not setting.check_capabilities()):
                return False
            # end if
        # end for
        section = self.manager.get_section(self.section)
        if (php_isset(lambda : section)) and (not section.check_capabilities()):
            return False
        # end if
        return True
    # end def check_capabilities
    #// 
    #// Get the control's content for insertion into the Customizer pane.
    #// 
    #// @since 4.1.0
    #// 
    #// @return string Contents of the control.
    #//
    def get_content(self):
        
        ob_start()
        self.maybe_render()
        return php_trim(ob_get_clean())
    # end def get_content
    #// 
    #// Check capabilities and render the control.
    #// 
    #// @since 3.4.0
    #// @uses WP_Customize_Control::render()
    #//
    def maybe_render(self):
        
        if (not self.check_capabilities()):
            return
        # end if
        #// 
        #// Fires just before the current Customizer control is rendered.
        #// 
        #// @since 3.4.0
        #// 
        #// @param WP_Customize_Control $this WP_Customize_Control instance.
        #//
        do_action("customize_render_control", self)
        #// 
        #// Fires just before a specific Customizer control is rendered.
        #// 
        #// The dynamic portion of the hook name, `$this->id`, refers to
        #// the control ID.
        #// 
        #// @since 3.4.0
        #// 
        #// @param WP_Customize_Control $this WP_Customize_Control instance.
        #//
        do_action(str("customize_render_control_") + str(self.id), self)
        self.render()
    # end def maybe_render
    #// 
    #// Renders the control wrapper and calls $this->render_content() for the internals.
    #// 
    #// @since 3.4.0
    #//
    def render(self):
        
        id = "customize-control-" + php_str_replace(Array("[", "]"), Array("-", ""), self.id)
        class_ = "customize-control customize-control-" + self.type
        printf("<li id=\"%s\" class=\"%s\">", esc_attr(id), esc_attr(class_))
        self.render_content()
        php_print("</li>")
    # end def render
    #// 
    #// Get the data link attribute for a setting.
    #// 
    #// @since 3.4.0
    #// @since 4.9.0 Return a `data-customize-setting-key-link` attribute if a setting is not registered for the supplied setting key.
    #// 
    #// @param string $setting_key
    #// @return string Data link parameter, a `data-customize-setting-link` attribute if the `$setting_key` refers to a pre-registered setting,
    #// and a `data-customize-setting-key-link` attribute if the setting is not yet registered.
    #//
    def get_link(self, setting_key="default"):
        
        if (php_isset(lambda : self.settings[setting_key])) and type(self.settings[setting_key]).__name__ == "WP_Customize_Setting":
            return "data-customize-setting-link=\"" + esc_attr(self.settings[setting_key].id) + "\""
        else:
            return "data-customize-setting-key-link=\"" + esc_attr(setting_key) + "\""
        # end if
    # end def get_link
    #// 
    #// Render the data link attribute for the control's input element.
    #// 
    #// @since 3.4.0
    #// @uses WP_Customize_Control::get_link()
    #// 
    #// @param string $setting_key
    #//
    def link(self, setting_key="default"):
        
        php_print(self.get_link(setting_key))
    # end def link
    #// 
    #// Render the custom attributes for the control's input element.
    #// 
    #// @since 4.0.0
    #//
    def input_attrs(self):
        
        for attr,value in self.input_attrs:
            php_print(attr + "=\"" + esc_attr(value) + "\" ")
        # end for
    # end def input_attrs
    #// 
    #// Render the control's content.
    #// 
    #// Allows the content to be overridden without having to rewrite the wrapper in `$this::render()`.
    #// 
    #// Supports basic input types `text`, `checkbox`, `textarea`, `radio`, `select` and `dropdown-pages`.
    #// Additional input types such as `email`, `url`, `number`, `hidden` and `date` are supported implicitly.
    #// 
    #// Control content can alternately be rendered in JS. See WP_Customize_Control::print_template().
    #// 
    #// @since 3.4.0
    #//
    def render_content(self):
        
        input_id = "_customize-input-" + self.id
        description_id = "_customize-description-" + self.id
        describedby_attr = " aria-describedby=\"" + esc_attr(description_id) + "\" " if (not php_empty(lambda : self.description)) else ""
        for case in Switch(self.type):
            if case("checkbox"):
                php_print("             <span class=\"customize-inside-control-row\">\n                 <input\n                        id=\"")
                php_print(esc_attr(input_id))
                php_print("\"\n                     ")
                php_print(describedby_attr)
                php_print("                     type=\"checkbox\"\n                     value=\"")
                php_print(esc_attr(self.value()))
                php_print("\"\n                     ")
                self.link()
                php_print("                     ")
                checked(self.value())
                php_print("                 />\n                    <label for=\"")
                php_print(esc_attr(input_id))
                php_print("\">")
                php_print(esc_html(self.label))
                php_print("</label>\n                   ")
                if (not php_empty(lambda : self.description)):
                    php_print("                     <span id=\"")
                    php_print(esc_attr(description_id))
                    php_print("\" class=\"description customize-control-description\">")
                    php_print(self.description)
                    php_print("</span>\n                    ")
                # end if
                php_print("             </span>\n               ")
                break
            # end if
            if case("radio"):
                if php_empty(lambda : self.choices):
                    return
                # end if
                name = "_customize-radio-" + self.id
                php_print("             ")
                if (not php_empty(lambda : self.label)):
                    php_print("                 <span class=\"customize-control-title\">")
                    php_print(esc_html(self.label))
                    php_print("</span>\n                ")
                # end if
                php_print("             ")
                if (not php_empty(lambda : self.description)):
                    php_print("                 <span id=\"")
                    php_print(esc_attr(description_id))
                    php_print("\" class=\"description customize-control-description\">")
                    php_print(self.description)
                    php_print("</span>\n                ")
                # end if
                php_print("\n               ")
                for value,label in self.choices:
                    php_print("                 <span class=\"customize-inside-control-row\">\n                     <input\n                            id=\"")
                    php_print(esc_attr(input_id + "-radio-" + value))
                    php_print("\"\n                         type=\"radio\"\n                            ")
                    php_print(describedby_attr)
                    php_print("                         value=\"")
                    php_print(esc_attr(value))
                    php_print("\"\n                         name=\"")
                    php_print(esc_attr(name))
                    php_print("\"\n                         ")
                    self.link()
                    php_print("                         ")
                    checked(self.value(), value)
                    php_print("                         />\n                        <label for=\"")
                    php_print(esc_attr(input_id + "-radio-" + value))
                    php_print("\">")
                    php_print(esc_html(label))
                    php_print("</label>\n                   </span>\n               ")
                # end for
                php_print("             ")
                break
            # end if
            if case("select"):
                if php_empty(lambda : self.choices):
                    return
                # end if
                php_print("             ")
                if (not php_empty(lambda : self.label)):
                    php_print("                 <label for=\"")
                    php_print(esc_attr(input_id))
                    php_print("\" class=\"customize-control-title\">")
                    php_print(esc_html(self.label))
                    php_print("</label>\n               ")
                # end if
                php_print("             ")
                if (not php_empty(lambda : self.description)):
                    php_print("                 <span id=\"")
                    php_print(esc_attr(description_id))
                    php_print("\" class=\"description customize-control-description\">")
                    php_print(self.description)
                    php_print("</span>\n                ")
                # end if
                php_print("\n               <select id=\"")
                php_print(esc_attr(input_id))
                php_print("\" ")
                php_print(describedby_attr)
                php_print(" ")
                self.link()
                php_print(">\n                  ")
                for value,label in self.choices:
                    php_print("<option value=\"" + esc_attr(value) + "\"" + selected(self.value(), value, False) + ">" + label + "</option>")
                # end for
                php_print("             </select>\n             ")
                break
            # end if
            if case("textarea"):
                php_print("             ")
                if (not php_empty(lambda : self.label)):
                    php_print("                 <label for=\"")
                    php_print(esc_attr(input_id))
                    php_print("\" class=\"customize-control-title\">")
                    php_print(esc_html(self.label))
                    php_print("</label>\n               ")
                # end if
                php_print("             ")
                if (not php_empty(lambda : self.description)):
                    php_print("                 <span id=\"")
                    php_print(esc_attr(description_id))
                    php_print("\" class=\"description customize-control-description\">")
                    php_print(self.description)
                    php_print("</span>\n                ")
                # end if
                php_print("             <textarea\n                 id=\"")
                php_print(esc_attr(input_id))
                php_print("\"\n                 rows=\"5\"\n                    ")
                php_print(describedby_attr)
                php_print("                 ")
                self.input_attrs()
                php_print("                 ")
                self.link()
                php_print("             >")
                php_print(esc_textarea(self.value()))
                php_print("</textarea>\n                ")
                break
            # end if
            if case("dropdown-pages"):
                php_print("             ")
                if (not php_empty(lambda : self.label)):
                    php_print("                 <label for=\"")
                    php_print(esc_attr(input_id))
                    php_print("\" class=\"customize-control-title\">")
                    php_print(esc_html(self.label))
                    php_print("</label>\n               ")
                # end if
                php_print("             ")
                if (not php_empty(lambda : self.description)):
                    php_print("                 <span id=\"")
                    php_print(esc_attr(description_id))
                    php_print("\" class=\"description customize-control-description\">")
                    php_print(self.description)
                    php_print("</span>\n                ")
                # end if
                php_print("\n               ")
                dropdown_name = "_customize-dropdown-pages-" + self.id
                show_option_none = __("&mdash; Select &mdash;")
                option_none_value = "0"
                dropdown = wp_dropdown_pages(Array({"name": dropdown_name, "echo": 0, "show_option_none": show_option_none, "option_none_value": option_none_value, "selected": self.value()}))
                if php_empty(lambda : dropdown):
                    dropdown = php_sprintf("<select id=\"%1$s\" name=\"%1$s\">", esc_attr(dropdown_name))
                    dropdown += php_sprintf("<option value=\"%1$s\">%2$s</option>", esc_attr(option_none_value), esc_html(show_option_none))
                    dropdown += "</select>"
                # end if
                #// Hackily add in the data link parameter.
                dropdown = php_str_replace("<select", "<select " + self.get_link() + " id=\"" + esc_attr(input_id) + "\" " + describedby_attr, dropdown)
                #// Even more hacikly add auto-draft page stubs.
                #// @todo Eventually this should be removed in favor of the pages being injected into the underlying get_pages() call. See <https://github.com/xwp/wp-customize-posts/pull/250>.
                nav_menus_created_posts_setting = self.manager.get_setting("nav_menus_created_posts")
                if nav_menus_created_posts_setting and current_user_can("publish_pages"):
                    auto_draft_page_options = ""
                    for auto_draft_page_id in nav_menus_created_posts_setting.value():
                        post = get_post(auto_draft_page_id)
                        if post and "page" == post.post_type:
                            auto_draft_page_options += php_sprintf("<option value=\"%1$s\">%2$s</option>", esc_attr(post.ID), esc_html(post.post_title))
                        # end if
                    # end for
                    if auto_draft_page_options:
                        dropdown = php_str_replace("</select>", auto_draft_page_options + "</select>", dropdown)
                    # end if
                # end if
                php_print(dropdown)
                php_print("             ")
                if self.allow_addition and current_user_can("publish_pages") and current_user_can("edit_theme_options"):
                    pass
                    php_print("                 <button type=\"button\" class=\"button-link add-new-toggle\">\n                     ")
                    #// translators: %s: Add New Page label.
                    printf(__("+ %s"), get_post_type_object("page").labels.add_new_item)
                    php_print("                 </button>\n                 <div class=\"new-content-item\">\n                      <label for=\"create-input-")
                    php_print(self.id)
                    php_print("\"><span class=\"screen-reader-text\">")
                    _e("New page title")
                    php_print("</span></label>\n                        <input type=\"text\" id=\"create-input-")
                    php_print(self.id)
                    php_print("\" class=\"create-item-input\" placeholder=\"")
                    esc_attr_e("New page title&hellip;")
                    php_print("\">\n                        <button type=\"button\" class=\"button add-content\">")
                    _e("Add")
                    php_print("</button>\n                  </div>\n                ")
                # end if
                php_print("             ")
                break
            # end if
            if case():
                php_print("             ")
                if (not php_empty(lambda : self.label)):
                    php_print("                 <label for=\"")
                    php_print(esc_attr(input_id))
                    php_print("\" class=\"customize-control-title\">")
                    php_print(esc_html(self.label))
                    php_print("</label>\n               ")
                # end if
                php_print("             ")
                if (not php_empty(lambda : self.description)):
                    php_print("                 <span id=\"")
                    php_print(esc_attr(description_id))
                    php_print("\" class=\"description customize-control-description\">")
                    php_print(self.description)
                    php_print("</span>\n                ")
                # end if
                php_print("             <input\n                    id=\"")
                php_print(esc_attr(input_id))
                php_print("\"\n                 type=\"")
                php_print(esc_attr(self.type))
                php_print("\"\n                 ")
                php_print(describedby_attr)
                php_print("                 ")
                self.input_attrs()
                php_print("                 ")
                if (not (php_isset(lambda : self.input_attrs["value"]))):
                    php_print("                     value=\"")
                    php_print(esc_attr(self.value()))
                    php_print("\"\n                 ")
                # end if
                php_print("                 ")
                self.link()
                php_print("                 />\n                ")
                break
            # end if
        # end for
    # end def render_content
    #// 
    #// Render the control's JS template.
    #// 
    #// This function is only run for control types that have been registered with
    #// WP_Customize_Manager::register_control_type().
    #// 
    #// In the future, this will also print the template for the control's container
    #// element and be override-able.
    #// 
    #// @since 4.1.0
    #//
    def print_template(self):
        
        php_print("     <script type=\"text/html\" id=\"tmpl-customize-control-")
        php_print(self.type)
        php_print("-content\">\n            ")
        self.content_template()
        php_print("     </script>\n     ")
    # end def print_template
    #// 
    #// An Underscore (JS) template for this control's content (but not its container).
    #// 
    #// Class variables for this control class are available in the `data` JS object;
    #// export custom variables by overriding WP_Customize_Control::to_json().
    #// 
    #// @see WP_Customize_Control::print_template()
    #// 
    #// @since 4.1.0
    #//
    def content_template(self):
        
        pass
    # end def content_template
# end class WP_Customize_Control
#// 
#// WP_Customize_Color_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-color-control.php", once=True)
#// 
#// WP_Customize_Media_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-media-control.php", once=True)
#// 
#// WP_Customize_Upload_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-upload-control.php", once=True)
#// 
#// WP_Customize_Image_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-image-control.php", once=True)
#// 
#// WP_Customize_Background_Image_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-background-image-control.php", once=True)
#// 
#// WP_Customize_Background_Position_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-background-position-control.php", once=True)
#// 
#// WP_Customize_Cropped_Image_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-cropped-image-control.php", once=True)
#// 
#// WP_Customize_Site_Icon_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-site-icon-control.php", once=True)
#// 
#// WP_Customize_Header_Image_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-header-image-control.php", once=True)
#// 
#// WP_Customize_Theme_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-theme-control.php", once=True)
#// 
#// WP_Widget_Area_Customize_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-widget-area-customize-control.php", once=True)
#// 
#// WP_Widget_Form_Customize_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-widget-form-customize-control.php", once=True)
#// 
#// WP_Customize_Nav_Menu_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-nav-menu-control.php", once=True)
#// 
#// WP_Customize_Nav_Menu_Item_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-nav-menu-item-control.php", once=True)
#// 
#// WP_Customize_Nav_Menu_Location_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-nav-menu-location-control.php", once=True)
#// 
#// WP_Customize_Nav_Menu_Name_Control class.
#// 
#// As this file is deprecated, it will trigger a deprecation notice if instantiated. In a subsequent
#// release, the require_once here will be removed and _deprecated_file() will be called if file is
#// required at all.
#// 
#// @deprecated 4.9.0 This file is no longer used due to new menu creation UX.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-nav-menu-name-control.php", once=True)
#// 
#// WP_Customize_Nav_Menu_Locations_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-nav-menu-locations-control.php", once=True)
#// 
#// WP_Customize_Nav_Menu_Auto_Add_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-nav-menu-auto-add-control.php", once=True)
#// 
#// WP_Customize_Date_Time_Control class.
#//
php_include_file(ABSPATH + WPINC + "/customize/class-wp-customize-date-time-control.php", once=True)