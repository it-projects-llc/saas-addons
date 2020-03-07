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
    var tree  = new Map()
    
    // Returns element index if element exist in choosen
    function includes_module(name){
        for(var i = 0; i < choosen.length; ++i){
            if(choosen[i].name === name) return i;
        }
        return -1;
    }

    // Finding all the links up to the tree,
    // and push them to delete_list
    delete_list = [];
    function leaf_to_root(name){
        if(!delete_list.includes(name))
            delete_list.push(name);
        roots = tree.get(name);
        if(roots === undefined)
            return;
        if(roots.length > 0){
            roots.forEach(function(root){
                delete_list.push(root);
                leaf_to_root(root);
            });
        }
    }

    window.onclick=function(e){
        if(window.location.pathname === "/price"){
            if(e.target.className.includes("application")){
                // Looking at choosen period
                var price_period = per_month ? 'month' : 'year';
                // Getting choosen module dependecies
                session.rpc('/what_dependencies', {
                    args: [e.target.innerText, price_period]
                }).then(function (result) {

                    /* Be carefull with dependecies when changing programm logic,
                    cause first dependence - is module himself*/
                    var i = 0, choosing_new = false;
                    for(; i < result.dependencies.length; ++i){
                        // Add new element to the dependencies tree, cause we'll restablish a path from leaf to the root
                        // when we'll have to delete one of leafs
                        if(i > 0){
                            modules_parents = tree.get(result.dependencies[i].name);
                            root_module_name = result.dependencies[i].parent;
                            leaf_name = result.dependencies[i].name;
                            if(modules_parents === undefined){
                                tree.set(leaf_name, [root_module_name]);
                                console.log("INFO:Added new leaf '"+leaf_name+"' with root module '"+root_module_name+"'.");
                            }
                            else if(!modules_parents.includes(root_module_name)){
                                modules_parents.push(root_module_name);
                                console.log("INFO:Added new root module '"+root_module_name+"' to leaf '"+leaf_name+"'.");
                            }
                            else{
                                console.log("WARNING:Root module '"+root_module_name+"' already in tree!");
                            }
                        }
                        leaf_name = result.dependencies[i].name;
                        if(includes_module(leaf_name) === -1)
                        {
                            choosen.push(result.dependencies[i]);
                            $(".application:contains('"+leaf_name+"')")[0].style.color = "green";
                            choosing_new = true;
                        }else{
                            if(choosing_new)
                                continue;
                            leaf_to_root(leaf_name);
                            delete_list.forEach(function(module){
                                choosen.splice(includes_module(module), 1);
                                $(".application:contains('"+module+"')")[0].style.color = "black";
                            });
                            delete_list = [];
                            break;
                        }
                    }
                });
            }else if(e.target.className.includes("nav-link") && (e.target.innerText === "Annually" || e.target.innerText === "Monthly")){
                // Check choosen period
                per_month = e.target.innerText === "Monthly" ? true : false;
            }
            price = Calc_Price();
            var period = per_month ? "month" : "year"; 
            $('#price')[0].innerHTML = '<h2 id="price" class="card-title pricing-card-title">$'+String(price)+
            ' <small class="text-muted">/ '+ period +'</small></h2>';
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

    function Calc_Price(){
        // Calculate general price
        price = 0;
        var users_price_period = per_month ? 12.5 : 10.0;
        for(var i = 0; i < choosen.length; ++i){
            price += choosen[i].price;
        }
        return price + parseInt($('#users')[0].value, 10)*users_price_period;
    }
});
