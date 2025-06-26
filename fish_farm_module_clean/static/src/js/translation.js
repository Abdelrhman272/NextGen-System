odoo.define('fish_farm_management.translation', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var rpc = require('web.rpc');

function translateInterface() {
    rpc.query({
        route: '/fish_farm/get_translations',
        params: {
            modules: ['fish_farm_management'],
            lang: session.user_context.lang
        }
    }).then(function(translations) {
        $('[data-i18n]').each(function() {
            var key = $(this).data('i18n');
            if (translations[key]) {
                $(this).text(translations[key]);
            }
        });
    });
}

function changeLanguage(langCode) {
    rpc.query({
        route: '/fish_farm/set_user_language',
        params: {lang_code: langCode}
    }).then(function() {
        window.location.reload();
    });
}

core.bus.on('web_client_ready', null, function() {
    translateInterface();
});

return {
    translateInterface: translateInterface,
    changeLanguage: changeLanguage
};

});