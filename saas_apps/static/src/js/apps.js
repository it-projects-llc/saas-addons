odoo.define('saas_apps.model', function (require){
    'use_strict';

    var session = require('web.session');

    var price = 0;
    var per_month = true;

    window.onclick=function(e){
        if(window.location.pathname === "/price" && e.target.id == "application")
            price_period = per_month ? 'month' : 'year';
            session.rpc('/what_dependencies', {
                args: [e.target.innerText, price_period]
            }).then(function (result) {
                console.log(result);
            });
    }

    function Calc_Price(){
        // Calculate general price
        var users_price_period = per_month ? 12.5 : 10.0;
        return price + parseInt(('#users')[0].value, 10)*users_price_period;
    }
});
