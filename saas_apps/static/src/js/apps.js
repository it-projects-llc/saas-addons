/* Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
 License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).*/

odoo.define('saas_apps.model', function (require){
    'use_strict';

    var session = require('web.session');
    var Widget = require('web.Widget');

    var price = 0;
    var per_month = false;
    /* Also need to add this https://odoo-development.readthedocs.io/en/latest/dev/pos/send-pos-orders-to-server.html#saving-removed-products-of-pos-order-module*/
    var choosen = new Map()
    var parent_tree  = new Map()
    var child_tree  = new Map()
    var prices  = new Map()

    function Calc_Price(){
        // Calculate general price
        price = 0;
        var users_price_period = per_month ? 12.5 : 10.0;
        for (var value of choosen.values()) {
            price += value;
        }
        return price + parseInt($('#users')[0].value, 10)*users_price_period;
    }

    // Finding all the links up to the parent_tree,
    // and push them to delete_list
    delete_list = [];
    function leaf_to_root(name){
        if(delete_list.includes(name)) 
            return;
        delete_list.push(name);
        roots = parent_tree.get(name);
        if(roots === undefined)
            return;
        if(roots.length > 0){
            roots.forEach(function(root){
                leaf_to_root(root);
            });
        }
    }

    leafs = [];
    function root_to_leafs(name){
        if(leafs.includes(name)) 
            return;
        leafs.push(name);
        deps = child_tree.get(name);
        if(deps === undefined)
            return;
        if(deps.length > 0){
            deps.forEach(function(leaf){
                root_to_leafs(leaf);
            });
        }
    }

    function add_price(module){
        var price = per_month ? module.month_price : module.year_price;
        $(".app_tech_name:contains('"+module.name+"')").filter(function(_, el) {
                return $(el).html() == module.name 
            })[0].previousElementSibling.children[1].innerText = ' / ' + String(price) + ' $';
        if(prices.get(module.name) === undefined)
            prices.set(module.name, [module.month_price, module.year_price])
    }

    window.onload = function() {
        var apps = $('.app_tech_name'), i = 0;
        for(; i < apps.length; ++i){
            session.rpc('/what_dependencies', {
                args: [apps[i].innerText]
            }).then(function (result) {
                /* Be carefull with dependecies when changing programm logic,
                cause first dependence - is module himself*/
                var i = 0;
                for(; i < result.dependencies.length; ++i){
                    // Add new element to the dependencies parent_tree, cause we'll restablish a path from leaf to the root
                    // when we'll have to delete one of leafs
                    if(i > 0){
                        var modules_parents = parent_tree.get(result.dependencies[i].name),
                            root_module_name = result.dependencies[i].parent,
                            leaf_name = result.dependencies[i].name;
                        if(modules_parents === undefined){
                            parent_tree.set(leaf_name, [root_module_name]);
                            console.log("INFO:Added new leaf '"+leaf_name+"' with root module '"+root_module_name+"'.");
                        }else if(!modules_parents.includes(root_module_name)){
                            modules_parents.push(root_module_name);
                            console.log("INFO:Added new root module '"+root_module_name+"' to leaf '"+leaf_name+"'.");
                        }else{
                            console.log("WARNING:Root module '"+root_module_name+"' already in parent_tree!");
                        }
                    }
                    if(result.dependencies[i].childs){
                        var root = result.dependencies[i].name, 
                            in_tree_childs = child_tree.get(root);
                            // Here we get new elements from result.dependencies[i].childs, difference btw
                            // result.dependencies[i].childs and in_tree_childs.
                        if(in_tree_childs === undefined){
                            child_tree.set(root, result.dependencies[i].childs);
                            console.log("INFO:Added new root '"+root+"' with childs '"+result.dependencies[i].childs[0]+"...'");
                        }else{
                            var new_childs = result.dependencies[i].childs.filter(x => !in_tree_childs.includes(x));
                            new_childs.forEach(function(child){
                                in_tree_childs.push(child);
                                console.log("INFO:Added new child module '"+child+"' to root '"+root+"'.");
                            });
                        }
                    }
                    
                    add_price(result.dependencies[i]);
                }
            });
        }
    };
    
    function add_to_basket(module_name){
        if(choosen.get(module_name) === undefined){
            var price = per_month ? prices.get(module_name)[0] : prices.get(module_name)[1];
            choosen.set(module_name, price),
                elem = $(".app_tech_name:contains('"+module_name+"')").filter(function(_, el) {
                    return $(el).html() == module_name 
                })
            elem[0].previousElementSibling.style.color = "green";
            elem[0].previousElementSibling.lastElementChild.style.opacity = 1;
        }
    }

    function delete_from_basket(module_name){
        if(choosen.get(module_name) !== undefined){
            choosen.delete(module_name),
            elem = $(".app_tech_name:contains('"+module_name+"')").filter(function(_, el) {
                return $(el).html() == module_name 
            })
        elem[0].previousElementSibling.style.color = "black";
        elem[0].previousElementSibling.lastElementChild.style.opacity = 0;
        }
    }

    window.onclick=function(e){
        if(window.location.pathname === "/price"){
            if(e.target.className.includes("app")){
                // App technical name
                var app = e.target.nextElementSibling.innerText;
                if(choosen.get(app) === undefined)
                {
                    root_to_leafs(app);
                    leafs.forEach(function(leaf){
                        add_to_basket(leaf);
                    });
                    leafs = [];
                }else{
                    leaf_to_root(app);
                    delete_list.forEach(function(module){
                        delete_from_basket(module);
                    });
                    delete_list = [];
                }
            }else if(e.target.className.includes("nav-link") && (e.target.innerText === "Annually" || e.target.innerText === "Monthly")){
                // Check choosen period
                per_month = e.target.innerText === "Monthly" ? true : false;
            }
            price = Calc_Price();
            var period = per_month ? "month" : "year";
            $('#price')[0].innerHTML = '<h4 id="price" class="card-title pricing-card-title">$'+String(price)+
            ' <small class="text-muted">/ '+ period +'</small></h4>';
        }
    }

    // var Price = Widget.extend({
    //     template: 'price.template',
    //     init: function(){
    //         this.$('p.app_tech_name').click(function() {
    //             // Looking at choosen period
    //             var price_period = per_month ? 'month' : 'year';
    //             var app_name = $('p.app_tech_name')[0].innerText;
    //             // Getting choosen module dependecies
    //             session.rpc('/what_dependencies', {
    //                 args: [app_name, price_period]
    //             }).then(function (result) {
    //                 console.log(result);
    //                 /* Be carefull with dependecies when changing programm logic,
    //                     cause first dependence - is module himself*/
    //                 var i = 0;
    //                 for(; i < result.dependencies.length; ++i) 
    //                     if(!choosen.includes(result.dependencies[i]))
    //                     {
    //                         choosen.push(result.dependencies[i]);
    //                         $(".app_tech_name:contains('"+result.dependencies[i]+"')")[0].style.color = "green";
    //                     }else{
    //                         choosen.splice(choosen.indexOf(result.dependencies[i]), 1);
    //                         if(i == 0){
    //                             $(".app_tech_name:contains('"+result.dependencies[i]+"')")[0].style.color = "black";
    //                             break;
    //                         }
    //                     }
    //             });
    //         });
    //     }
    // });
});
