odoo.define('saas_apps.model', function (require){
    'use_strict';

    var session = require('web.session');

    
    // function poopup_widjet(args){
        
    // }

    window.onclick=function(e){
        console.log(e.target.innerText);

        if(window.location.pathname === "/manage")
            session.rpc('/test', {
                args: [e.target.innerText]
            }).then(function (result) {
                console.log(result);
                // poopup_widjet(result);
            });
    }
});
