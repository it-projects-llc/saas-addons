/* Copyright 2020 Vildan Safin <https://www.it-projects.info/team/Enigma228322>
 License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).*/
odoo.define('saas_apps.model', function (require) {
    'use_strict';

    var session = require('web.session');
    var Widget = require('web.Widget');

    var price = 0,
        per_month = false,
        choosen = new Map(),
        parent_tree = new Map(),
        child_tree = new Map(),
        apps_in_basket = 0,
        currency = "",
        currency_symbol = "";

    function calc_apps_price() {
        price = 0;
        for (var value of choosen.values()) {
            price += value;
        }
        return price;
    }

    function user_price() {
        return per_month ? 12.5 : 10.0;
    }

    function Calc_Price() {
        // Calculate general price
        if($('#users')[0] !== undefined)
            return calc_apps_price() + parseInt($('#users')[0].value, 10) * user_price();
        return 0;
    }

    function get_choosen_package() {
        var packages = [];
        $.each($('.package'), function (index, value) {
            packages.push(value.children[2].innerText);
        });
        for (var key of choosen.keys()) {
            if (packages.includes(key)) {
                return key;
            }
        }
    }

    function redirect_to_build(modules_to_install) {
        // Checking for choosen packages
        var package = get_choosen_package();
        // If the package selected, we'll use packages saas_template to create build
        if (!package) {
            // If package wasn't selected, then collect choosen modules
            if (!modules_to_install) {
                modules_to_install = '?installing_modules=['
                // Collecting choosen modules in string
                for (var key of choosen.keys()) {
                    modules_to_install += ','
                    modules_to_install += '"' + String(key) + '"';
                }
                modules_to_install += ']';
                // Deleting extra coma
                modules_to_install = modules_to_install.replace(',', '');
            }
            if (!choosen.size) {
                alert("You haven't chosen any application!")
                return;
                // modules_to_install = '?installing_modules=["mail"]';
            }
        }
        go_to_build(modules_to_install, package);
    }

    function go_to_build(modules_to_install, package) {
        // Checking for choosen packages
        if (package) modules_to_install = '';
        session.rpc('/take_template_id', {
            package: package
        }).then(function (template) {
            if (template.state === 'ready') {
                console.log("Redirect to: " + "/saas_public/" + template.id + "/create-fast-build" + modules_to_install);
                // When there's ready saas_template_operator obj, then start creating new build
                window.location.href = "/saas_public/" + template.id + "/create-fast-build" + modules_to_install;
            } else {
                // If there's no ready saas_template_operator,
                // recalling this func till the saas_template_operator obj isn't ready
                setTimeout(redirect_to_build, 5000, modules_to_install, package);
            }
        });
    }

    function redirect_to_cart() {
        var modules = [];
        for (var key of choosen.keys()) {
            modules.push(key);
        }
        if (!modules) {
            alert("You haven't chosen any application!")
            return;
        }
        // Getting product ids
        session.rpc('/price/take_product_ids', {
            module_names: modules
        }).then(function (product_ids) {
            // If ids are know, redirect to cart
            session.rpc('/price/cart_update', {
                product_ids: product_ids.ids,
                old_apps_ids: get_old_products(),
                period: per_month ? 'm' : 'y',
                user_price: user_price(),
                old_user_cnt: get_old_user_cnt(),
                user_cnt: $('#users').val()
            }).then(function (response) {
                window.location.href = response.link;
            });
            // This method is necessary, to delete old products from cart
            save_old_products(product_ids.ids);
        });
    }

    // Finding all the links up to the parent_tree,
    // and push them to delete_list
    delete_list = [];
    function leaf_to_root(name) {
        if (delete_list.includes(name))
            return;
        delete_list.push(name);
        roots = parent_tree.get(name);
        if (roots === undefined)
            return;
        if (roots.length > 0) {
            roots.forEach(function (root) {
                leaf_to_root(root);
            });
        }
    }

    leafs = [];
    function root_to_leafs(name) {
        if (leafs.includes(name))
            return;
        leafs.push(name);
        deps = child_tree.get(name);
        if (deps === undefined)
            return;
        if (deps.length > 0) {
            deps.forEach(function (leaf) {
                root_to_leafs(leaf);
            });
        }
    }

    // Downloading apps dependencies
    window.onload = function () {
        // Check needs to avoid js code loading on another pages
        if (!window.location.pathname.includes('/price'))
            return;
        // Catching click to the app
        $(".app").click(function () {
            // Get app technical name
            var app = this.children[2].innerText;
            // If app isn't in basket right now, put it in
            if (choosen.get(app) === undefined) {
                // Get app dependencies and add them to the basket
                root_to_leafs(app);
                leafs.forEach(function (leaf) {
                    add_to_basket(leaf);
                });
                leafs = [];
            } else {
                // Get app dependencies and take them off from the basket
                leaf_to_root(app);
                delete_list.forEach(function (module) {
                    delete_from_basket(module);
                });
                delete_list = [];
            }
            calc_price_window_vals();
        });
        // Catching click to the 'Annually' button
        $(".nav-link:contains('Annually')").click(function () {
            per_month = false;
            change_period();
        });
        // Catching click to the 'Monthly' button
        $(".nav-link:contains('Monthly')").click(function () {
            per_month = true;
            change_period();
        });
        // Catching click to the 'Try trial' button
        $("#get-started").click(function () {
            // Showing the loader
            $('.loader')[0].classList.remove('hid');
            redirect_to_build(null, null);
        });
        // Catching click to the 'Buy now' button
        $("#buy-now").click(function () {
            // Showing the loader
            redirect_to_cart();
        });

        $('#users').click(function () {
            calc_price_window_vals();
        });
        $('#users').keyup(function (event) {
            if (event.keyCode === 13) {
                calc_price_window_vals();
            }
        });
        // Changing users qty buttons
        $('#substr-users').click(function () {
            check_users_input();
            $('#users').val(parseInt($('#users').val(), 10) - 1);
            calc_price_window_vals();
        });
        $('#add-users').click(function () {
            check_users_input();
            $('#users').val(parseInt($('#users').val(), 10) + 1);
            calc_price_window_vals();
        });

        session.rpc('/check_currency', {
        }).then(function (result) {
            currency = result.currency;
            currency_symbol = result.symbol;
        });

        // Check session storage
        old_modules = get_modules_from_session_storage();
        if (old_modules.length) {
            old_modules.forEach(elem => {
                add_to_basket(elem);
            });
            calc_price_window_vals();
        }
        // Activate loader
        $('.loader')[0].classList.remove('hid');

        // Counting reqests and answers
        var requests_stack = 0;
        $.each($('.app_tech_name'), function (key, app) {
            ++requests_stack;
            session.rpc('/what_dependencies', {
                root: [app.innerText]
            }).then(function (result) {
                --requests_stack;
                if (requests_stack < 5) {
                    $('.loader')[0].classList.add('hid');
                }
                /* Be carefull with dependecies when changing programm logic,
                cause first dependence - is module himself.
                Now result contains app's themself and their dependencies,
                now parse incoming data in child and parent tree, to save dependencies.*/
                var first_dependence = true;
                result.dependencies.forEach(dependence => {
                    // Add new element to the dependencies parent_tree, cause we'll restablish a path from leaf to the root
                    // when we'll have to delete one of leafs
                    if (!first_dependence) {
                        var modules_parents = parent_tree.get(dependence.name),
                            root_module_name = dependence.parent,
                            leaf_name = dependence.name;
                        if (modules_parents === undefined) {
                            parent_tree.set(leaf_name, [root_module_name]);
                            console.log("INFO:Added new leaf '" + leaf_name + "' with root module '" + root_module_name + "'.");
                        } else if (!modules_parents.includes(root_module_name)) {
                            modules_parents.push(root_module_name);
                            console.log("INFO:Added new root module '" + root_module_name + "' to leaf '" + leaf_name + "'.");
                        } else {
                            console.log("WARNING:Root module '" + root_module_name + "' already in parent_tree!");
                        }
                    }
                    if (dependence.childs) {
                        var root = dependence.name,
                            in_tree_childs = child_tree.get(root);
                        // Here we get new elements from dependence.childs, difference btw
                        // dependence.childs and in_tree_childs.
                        if (in_tree_childs === undefined) {
                            child_tree.set(root, dependence.childs);
                            console.log("INFO:Added new root '" + root + "' with childs '" + dependence.childs[0] + "...'");
                        } else {
                            var new_childs = dependence.childs.filter(x => !in_tree_childs.includes(x));
                            new_childs.forEach(function (child) {
                                in_tree_childs.push(child);
                                console.log("INFO:Added new child module '" + child + "' to root '" + root + "'.");
                            });
                        }
                    }

                    first_dependence = false;
                });
            });
        });
        if (requests_stack === 0) {
            $('.loader')[0].classList.add('hid');
        }
    };

    function change_border_color(elem) {
        if (elem.classList.contains('green-border')) {
            elem.classList.add('normal-border');
            elem.classList.remove('green-border');
        } else {
            elem.classList.add('green-border');
            elem.classList.remove('normal-border');
        }
    }

    function change_period() {
        var i = 0,
            monthly = $('.monthly-price'),
            yearly = $('.yearly-price'),
            n = yearly.length;
        if (per_month) {
            for (; i < n; ++i) {
                monthly[i].classList.remove('hid');
                yearly[i].classList.add('hid');
            }
        }
        else {
            for (; i < n; ++i) {
                monthly[i].classList.add('hid');
                yearly[i].classList.remove('hid');
            }
        }
        var size = choosen.size, i = 0;
        for (var key of choosen.keys()) {
            if (i >= size) break;
            delete_from_basket(key);
            add_to_basket(key);
            ++i;
        }
        calc_price_window_vals();
    }

    function check_for_packages(module_name) {
        if (choosen.size == 0) {
            return;
        }
        // Collect all packages names in array
        var packages = [];
        $.each($('.package'), function (index, value) {
            packages.push(value.children[2].innerText);
        });
        // if package choosen, then delete other products from cart
        if (packages.includes(module_name)) {
            for (var key of choosen.keys()) {
                delete_from_basket(key);
            }
            choosen.clear();
        }
        else {
            // If app choosen, then delete package from cart
            for (var key of choosen.keys()) {
                if (packages.includes(key)) {
                    delete_from_basket(key);
                    return;
                }
            }
        }
    }

    function add_to_basket(module_name) {
        check_for_packages(module_name);
        if (choosen.get(module_name) === undefined) {
            // Finding choosen element
            elem = $(".app_tech_name:contains('" + module_name + "')").filter(function (_, el) {
                return $(el).html() == module_name
            })
            price = 0;
            // Get choosen app price
            if (elem.length > 0) {
                price_i = per_month ? 1 : 0;
                price = parseInt(elem[0].previousElementSibling.children[1].children[price_i].children[0].innerText, 10);
                // Changing border color
                ++apps_in_basket;
                change_border_color(elem[0].parentElement);
            }
            // Insert new app in to the basket
            choosen.set(module_name, price);
            save_modules_to_session_storage();
        }
    }

    function delete_from_basket(module_name) {
        if (choosen.get(module_name) !== undefined) {
            // Delete app from the basket
            choosen.delete(module_name);
            // Finding choosen element
            elem = $(".app_tech_name:contains('" + module_name + "')").filter(function (_, el) {
                return $(el).html() == module_name
            })
            // Changing border color
            if (elem.length > 0) {
                --apps_in_basket;
                change_border_color(elem[0].parentElement);
            }
        }
        save_modules_to_session_storage();
    }

    function blink_anim(elems) {
        elems.forEach((elem) => {
            elem.animate({ opacity: "0" }, 250);
            elem.animate({ opacity: "1" }, 250);
        });
    }

    function calc_price_window_vals() {
        check_users_input();
        // This method refreshes data in price window
        price = Calc_Price();
        // Adding blink animation
        blink_anim([$('#apps-cost'), $('#users-cnt-cost'),
        $('#apps-qty'), $('#price-users'), $('#users-qty'), $('#price')]);
        var period = per_month ? "month" : "year";
        $('#price').text(String(price) + ' ' + currency_symbol + ' / ');
        $('#box-period').text(String(period));
        $('#users-qty').text($('#users').val())
        users_price_period = per_month ? 12.5 : 10.0;
        $('#price-users').text(String(users_price_period));
        $('#apps-qty').text(String(apps_in_basket));
        $('#users-cnt-cost').text(String(users_price_period * $('#users').val()));
        $('#apps-cost').text(String(calc_apps_price()));
    }

    function check_users_input() {
        if (parseInt($('#users').val(), 10) <= 0 || $('#users').val() === '')
            $('#users').val(1);
    }

    function get_modules_to_install() {
        var modules = [];
        for (var key of choosen.keys()) {
            modules.push(key);
        }
        return modules;
    }

    function save_old_products(ids) {
        localStorage.removeItem('old_user_cnt');
        localStorage.removeItem('old_products');
        localStorage.setItem('old_products', ids);
        localStorage.setItem('old_user_cnt', $('#users').val());
    }

    function get_old_user_cnt() { return localStorage.getItem('old_user_cnt'); }

    function get_old_products() {
        return parse_string_to_arr(localStorage.getItem('old_products'));
    }

    function save_modules_to_session_storage() {
        localStorage.removeItem('modules');
        localStorage.setItem('modules', get_modules_to_install());
    }

    function parse_string_to_arr(str) {
        if (str) {
            var i = 0, j = 1, arr = [];
            for (; j < str.length; ++j) {
                if (str[j] === ',') {
                    arr.push(str.slice(i, j));
                    i = j + 1;
                    j += 2;
                }
            }
            arr.push(str.slice(i, j));
            return arr;
        }
        return [];
    }

    function get_modules_from_session_storage() {
        return parse_string_to_arr(localStorage.getItem('modules'));
    }

    return {
        "get_modules_to_install": get_modules_to_install,
    }
});
