odoo.define("saas_apps.saas_apps", function (require) {
    "use strict";

    require('web.dom_ready');

    var session = require('web.session');

    if (!$(".js_saas_apps").length) {
        return Promise.reject("DOM doesn't contain '.js_saas_apps'");
    }

    var MONTHLY = "month";
    var ANNUALLY = "year";
    var basket_apps = new Set();
    var chosen_package_id = null;;
    var period = ANNUALLY;

    // Задаем свойства вида depends-<MODULE_NAME>=1
    $(".app[data-depends]").each(function(i, el) {
        var $el = $(el);
        $el.data("depends").split(",").filter(Boolean).forEach(function(depend) {
            $el.data("depends-" + depend, 1);
        });
    });

    function getAppNameByElementCallback(i, el) {
        return $(el).data("name");
    }

    function renderTotalPrice() {
        function priceCallback(i, el) {
            return parseFloat($(el).data("price-" + period) || 0);
        }

        var chosen_apps = $(".app").filter(function(i, el) {
            return basket_apps.has(getAppNameByElementCallback(i, el));
        });

        var chosen_apps_prices = chosen_apps.map(priceCallback).get();

        // Тут вполне допускается вариант, что выбрали несколько пакетов
        // Хотя функциолом это не продусмотрено
        var chosen_packages = $(".package").filter(function(i, el) {
            return $(el).data("package-id") === chosen_package_id;
        });

        var chosen_packages_prices = chosen_packages.map(priceCallback).get();

        var sum_app_prices = _.reduce(chosen_apps_prices, function(a, c) {
            return a + c;
        }, 0);

        var sum_package_prices = _.reduce(chosen_packages_prices, function(a, c) {
            return a + c;
        }, 0);

        var user_qty = parseInt($("#users").val(), 10);
        var sum_user_prices = user_qty * parseFloat($("#users_block").data("price-" + period));

        $("#price").html((sum_app_prices + sum_package_prices + sum_user_prices).toString());
        $("#box-period").html(period);
        $("#users-qty").html(user_qty);
        $("#users-cnt-cost").html(sum_user_prices);
        // TODO: надо бы отдельно вписать package, нет?
        $("#apps-qty").html(chosen_apps.length + chosen_packages.length);
        $("#apps-cost").html(sum_app_prices + sum_package_prices);

        if (chosen_packages.length === 0 && chosen_apps.length === 0) {
            $("#btn-block").hide();
        } else {
            $("#btn-block").show();
        }
    }

    function renderApps() {
        $(".app").each(function(i, el) {
            var $app = $(el);
            if (basket_apps.has($app.data("name"))) {
                $app.addClass("green-border");
            } else {
                $app.removeClass("green-border");
            }
        });
    }

    function renderPackages() {
        $(".package:not([data-package-id=" + chosen_package_id + "])").removeClass("green-border");
        $(".package[data-package-id=" + chosen_package_id + "]").addClass("green-border");
    }

    $(".app").on("click", function() {
        chosen_package_id = null;
        var $el = $(this);
        var name = $el.data("name");
        if (basket_apps.has(name) === false) {
            basket_apps.add(name);
            var app_names_to_select = $el
                .data("depends")
                .split(",")
                .filter(Boolean)  // take away falsy values
                .concat([name]);
            app_names_to_select.forEach(function(app_name) {
                basket_apps.add(app_name);
            });
        } else {
            var app_names_to_deselect = [name];
            while (app_names_to_deselect.length > 0) {
                var app_names_to_deselect_next = [];
                app_names_to_deselect.forEach(function(app_name) {
                    // Remove from basket
                    basket_apps.delete(app_name);

                    // Find other apps that depend on this
                    app_names_to_deselect_next = app_names_to_deselect_next.concat(
                        $(".app:data(depends-" + app_name + ")").map(getAppNameByElementCallback).get()
                    );
                });
                app_names_to_deselect = app_names_to_deselect_next;
            }
        }
        renderApps();
        renderTotalPrice();
    });

    $(".package").on("click", function() {
        basket_apps.clear();
        var $el = $(this);
        var package_id = $el.data("package-id");

        if (chosen_package_id === package_id) {
            chosen_package_id = null;
        } else {
            chosen_package_id = package_id;
        }

        renderApps();
        renderPackages();
        renderTotalPrice();
    });

    function sanitizeUserInput() {
        var v = $("#users").val();
        if (parseInt(v, 10) <= 0 || v.trim() === "") {
            $("#users").val(1);
        }
    }

    function getInputs() {
        sanitizeUserInput();
        return {
            chosen_apps: Array.from(basket_apps),
            chosen_package_id: chosen_package_id,
            period: period,
            user_cnt: parseInt($("#users").val(), 10),
        };
    }

    function goToBuild(build_params, template_id) {
        session.rpc('/check_saas_template', {
            template_id: template_id
        }).then(function(template) {
            if (template.state === 'ready') {
                var url = "/saas_public/" + template.id + "/create-fast-build" + build_params;
                console.log("Redirect to: " + url);
                // When there's ready saas_template_operator obj, then start creating new build
                window.location.href = url;
            } else {
                // If there's no ready saas_template_operator,
                // recalling this func till the saas_template_operator obj isn't ready
                setTimeout(goToBuild, 5000, build_params, template_id);
            }
        });
    }

    $("#minus-user").on("click", function() {
        sanitizeUserInput();
        var v = parseInt($("#users").val(), 10);
        $("#users").val(Math.max(1, v - 1));
        renderTotalPrice();
    });

    $("#plus-user").on("click", function() {
        sanitizeUserInput();
        var v = parseInt($("#users").val(), 10);
        $("#users").val(v + 1);
        renderTotalPrice();
    });

    $("#try-trial").on("click", function() {
        if (basket_apps.size > 0) {
            var build_params = '?installing_modules=["' + Array.from(basket_apps).join('","') + '"]';
            goToBuild(build_params);
            $(".loader").show();
        } else if (chosen_package_id) {
            goToBuild("", parseInt(chosen_package_id, 10));
            $(".loader").show();
        } else {
            alert("Please, choose apps or package first");
        }
    });

    $("#buy-now").on("click", function() {
        var product_ids = [];
        if (basket_apps.size > 0) {
            product_ids = Array.from(basket_apps).map(function(m) {
                return $("[data-name=" + m + "]").data("product-id-" + period);
            });
        } else if (chosen_package_id) {
            product_ids = [$("[data-package-id=" + chosen_package_id + "]").data("product-id-" + period)];
        } else {
            alert("Please, choose apps or package first");
            return;
        }

        session.rpc("/price/cart/update_json", {
            product_ids: product_ids,
            period: period,
            user_cnt: parseInt($("#users").val(), 10),
        }).then(function(res) {
            window.location.href = res.link;
        });
    });

    $(".switch-period").on("click", function() {
        period = $(this).data("period");
        renderTotalPrice();
    });

    renderTotalPrice();

    return {
        getInputs: getInputs,
    };
});
