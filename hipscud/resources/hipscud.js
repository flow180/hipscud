if (typeof HC !== 'undefined') {
    HipScud = {
        default_icon: 'https://hipchat-magnolia-cdn.atlassian.com/assets/img/hipchat/bookmark-icons/apple-touch-icon-57x57.png',
        unloaded: true,
        reload: window.location.reload.bind(window.location),
        didFinishLoading: function() {
            HipScud.populate();
            desktop.enableMenus(true);
            HipScud.unloaded = false;
        },
        setBadgeCount: function(unread, highlight) {
            var id = HipScud.getId();
            if (!id) return setTimeout(HipScud.setBadgeCount.bind(HipScud, unread, highlight), 500);
            else desktop.count(id, unread, highlight || false);
        },
        getId: function() {
            if (HC.ApplicationStore.data.group_id) return HC.ApplicationStore.data.group_id.toString();
        },
        log: function(name, args) {
            if ("object" == typeof(args)) args = JSON.stringify(args);
            console.log("HipScud." + name + ", args: " + args);
        },
        populate: function() {
            if (!HC.ApplicationStore.data.group_name || HC.ApplicationStore.data.group_name == '') {
                // Sometimes app-ready-state fires too early
                return setTimeout(HipScud.populate, 500);
            }
            var data = JSON.stringify({
                'channels': HipScud.listChannels(),
                'teams': HipScud.listTeams(),
                'icon': HC.ApplicationStore.data.config.group_avatar_url || HipScud.default_icon
            })
            desktop.populate(data);
        },
        listChannels: function() {
            var activeChats = HC.api.getActiveChats();
            var allRooms = HC.ApplicationStore.data.allRooms;
            return Object.keys(allRooms).map(function(id) {
                return {
                    id: id,
                    name: activeChats[id].name,
                    is_member: Object.keys(activeChats).indexOf(id) != -1
                };
            });
        },
        listTeams: function() {
            var list = [{
                id: HipScud.getId(),
                team_name: HC.ApplicationStore.data.group_name,
                team_url: window.location.href,
                team_icon: HC.ApplicationStore.data.config.group_avatar_url || HipScud.default_icon
            }];
            return list;
        },
        quicklist: function() {
            desktop.quicklist(HipScud.listChannels());
        },
        open: function(c) {
            return HC.Actions.RoomNavActions.select(c, 'groupchat');
        },
        preferences: function() {
            HC.Actions.DialogActions.showSettingDialog()
        },
        logout: function() {
            HC.Actions.AppActions.signout()
        }
    };

    /* Mock Notification because QWebkit doesn't have it */
    window.Notification = function(title, options) {
        desktop.sendMessage(title, options.body);
    }
    window.Notification.permission = 'granted';

    if (HipScud.unloaded) {
        HC.AppDispatcher.register('app-state-ready', HipScud.didFinishLoading);
        HC.Actions.AppActions.notifier.updateTotalUnreadCount = HipScud.setBadgeCount;
    }
}

function addSelfHostedOption() {
    if (!$('.sign-up-instead').length) return;
    var useServerLink = $('<a href="javascript:;">Using Hipchat Server?</a>');
    $(useServerLink).click(function() {
        var url = prompt('Enter the domain name of your Hipchat Server');
        window.location.replace('https://' + url + '/sign_in');
    });
    jQuery('.sign-up-instead').html('');
    jQuery('.sign-up-instead').append(useServerLink);
}
