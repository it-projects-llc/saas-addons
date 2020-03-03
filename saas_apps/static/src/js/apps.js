/* Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
 License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).*/

odoo.define('saas_apps.model', function (require){
    'use_strict';

    var session = require('web.session');

    var price = 0;
    var per_month = false;
    /* Also need to add this https://odoo-development.readthedocs.io/en/latest/dev/pos/send-pos-orders-to-server.html#saving-removed-products-of-pos-order-module*/
    var choosen = []
    
    window.onclick=function(e){
        if(window.location.pathname === "/price"){
            if(e.target.className.includes("application")){
                // Looking at choosen period
                var price_period = per_month ? 'month' : 'year';
                // Getting choosen module dependecies
                session.rpc('/what_dependencies', {
                    args: [e.target.innerText, price_period]
                }).then(function (result) {
                    console.log(result);
                    /* Be carefull with dependecies when changing programm logic,
                        cause first dependence - is module himself*/
                    var i = 0;
                    for(; i < result.dependencies.length; ++i) 
                        if(!choosen.includes(result.dependencies[i]))
                        {
                            choosen.push(result.dependencies[i]);
                            $(".application:contains('"+result.dependencies[i]+"')")[0].style.color = "green";
                        }else{
                            choosen.splice(choosen.indexOf(result.dependencies[i]), 1);
                            if(i == 0){
                                $(".application:contains('"+result.dependencies[i]+"')")[0].style.color = "black";
                                break;
                            }
                        }
                });
            }else if(e.target.className.includes("nav-link") && (e.target.innerText === "Annually" || e.target.innerText === "Monthly")){
                // Check choosen period
                per_month = e.target.innerText === "Monthly" ? true : false;
            }
        }
    }

    // $('p.application').click(function() {
    //     // Looking at choosen period
    //     var price_period = per_month ? 'month' : 'year';
    //     var app_name = $('p.application')[0].innerText;
    //     // Getting choosen module dependecies
    //     session.rpc('/what_dependencies', {
    //         args: [app_name, price_period]
    //     }).then(function (result) {
    //         console.log(result);
    //         /* Be carefull with dependecies when changing programm logic,
    //             cause first dependence - is module himself*/
    //         var i = 0;
    //         for(; i < result.dependencies.length; ++i) 
    //             if(!choosen.includes(result.dependencies[i]))
    //             {
    //                 choosen.push(result.dependencies[i]);
    //                 $(".application:contains('"+result.dependencies[i]+"')")[0].style.color = "green";
    //             }else{
    //                 choosen.splice(choosen.indexOf(result.dependencies[i]), 1);
    //                 if(i == 0){
    //                     $(".application:contains('"+result.dependencies[i]+"')")[0].style.color = "black";
    //                     break;
    //                 }
    //             }
    //     });
    // });

    function Calc_Price(){
        // Calculate general price
        var users_price_period = per_month ? 12.5 : 10.0;
        return price + parseInt(('#users')[0].value, 10)*users_price_period;
    }
});
