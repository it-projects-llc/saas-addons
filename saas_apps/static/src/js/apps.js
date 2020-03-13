/* Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
 License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).*/

odoo.define('saas_apps.model', function (require){
    'use_strict';

    var session = require('web.session');
    var Widget = require('web.Widget');

    var price = 0;
    var per_month = false;
    /* Also need to add this https://odoo-development.readthedocs.io/en/latest/dev/pos/send-pos-orders-to-server.html#saving-removed-products-of-pos-order-module*/
    var choosen = []
    var parent_tree  = new Map()
    var child_tree  = new Map()
    var prices  = new Map()
    
    // Returns element index if element exist in choosen
    function includes_module(name){
        for(var i = 0; i < choosen.length; ++i){
            if(choosen[i].name === name) return i;
        }
        return -1;
    }

    function Calc_Price(){
        // Calculate general price
        price = 0;
        var users_price_period = per_month ? 12.5 : 10.0;
        for(var i = 0; i < choosen.length; ++i){
            price += choosen[i].price;
        }
        return price + parseInt($('#users')[0].value, 10)*users_price_period;
    }

    // Finding all the links up to the parent_tree,
    // and push them to delete_list
    delete_list = [];
    function leaf_to_root(name){
        if(!delete_list.includes(name) )
            delete_list.push(name);
        roots = parent_tree.get(name);
        if(roots === undefined)
            return;
        if(roots.length > 0){
            roots.forEach(function(root){
                delete_list.push(root);
                leaf_to_root(root);
            });
        }
    }

    leafs = [];
    function root_to_leafs(name){
        if(!leafs.includes(name) )
            leafs.push(name);
        deps = child_tree.get(name);
        if(deps === undefined)
            return;
        if(deps.length > 0){
            deps.forEach(function(leaf){
                leafs.push(leaf);
                root_to_leafs(leaf);
            });
        }
    }

    window.onload = function() {
        var apps = $('.application'), i = 0;
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
                    if(prices.get(result.dependencies[i].name) === undefined)
                        prices.set(result.dependencies[i].name, [result.dependencies[i].month_price, result.dependencies[i].year_price])
                }
            });
        }
    };

    window.onclick=function(e){
        if(window.location.pathname === "/price"){
            if(e.target.className.includes("application")){
                var app = e.target.innerText;
                if(includes_module(app) === -1)
                {
                    root_to_leafs(app);
                    leafs.forEach(function(leaf){
                        choosen.push({
                            'name': leaf,
                            'price': per_month ? prices.get(leaf)[0] : prices.get(leaf)[1]
                        });
                        $(".application:contains('"+leaf+"')")[0].style.color = "green";
                    });
                    leafs = [];
                }else{
                    leaf_to_root(app);
                    delete_list.forEach(function(module){
                        var delete_id = includes_module(module);
                        if(delete_id !== -1){
                            choosen.splice(includes_module(module), 1);
                            $(".application:contains('"+module+"')")[0].style.color = "black";
                        }
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
    //         this.$('p.application').click(function() {
    //             // Looking at choosen period
    //             var price_period = per_month ? 'month' : 'year';
    //             var app_name = $('p.application')[0].innerText;
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
    //                         $(".application:contains('"+result.dependencies[i]+"')")[0].style.color = "green";
    //                     }else{
    //                         choosen.splice(choosen.indexOf(result.dependencies[i]), 1);
    //                         if(i == 0){
    //                             $(".application:contains('"+result.dependencies[i]+"')")[0].style.color = "black";
    //                             break;
    //                         }
    //                     }
    //             });
    //         });
    //     }
    // });
});
