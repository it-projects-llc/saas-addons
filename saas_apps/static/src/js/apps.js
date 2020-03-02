odoo.define('saas_apps.model', function (require){
    'use_strict';

    var session = require('web.session');

    window.onclick=function(e){
        if(window.location.pathname === "/price" && e.target.id == "application")
            session.rpc('/what_dependencies', {
                args: [e.target.innerText]
            }).then(function (result) {
                console.log(result);
            });
    }
});
