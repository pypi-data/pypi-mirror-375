/**
 * Module for reporting and requesting updates to installed YANG Suite plugins.
 */
let plugins = function() {
    /**
     * Default configuration of this module.
     */
    let config = {
        corePluginTable: 'table tbody#core-plugins',
        extraPluginTable: 'table tbody#extra-plugins',
        availablePluginTable: 'table tbody#available-plugins',

        anyPluginTable: 'table tbody#core-plugins, table tbody#extra-plugins, table tbody#available-plugins',
    };

    let c = config;    // internal alias for brevity

    function tableForPackage(packageName) {
        let corePlugins = [
            'yangsuite',
            'yangsuite-filemanager',
            'yangsuite-devices',
            'yangsuite-yangtree',
        ];
        if (corePlugins.includes(packageName)) {
            return $(c.corePluginTable);
        } else {
            return $(c.extraPluginTable);
        }
    };

    /**
     * Get the plugin list from the server and update the pluginTable.
     */
    function getInstalledPlugins() {
        return $.ajax({
            url: "/api/yangsuite/plugins/installed",
            type: 'GET',
            datatype: 'json',
            success: function(retObj) {
                let plugin_error = false;
                $(c.anyPluginTable).empty();
                for (let e of retObj) {
                    let tbody = tableForPackage(e.package_name);
                    let tr = $('<tr data-value="' + e.package_name + '">' +
                               '<td colspan="2"><code>' + e.package_name + '</code></td>' +
                               '<td class="description">' + e.description +
                               '</td><td class="plugin-installed-cell">' +
                               "<code>" + e.installed_version + "</code>" +
                               '</td><td class="plugin-latest-cell">' +
                               `<input type="checkbox" id=${e.package_name}-install-pre data-package="${e.package_name}">` +
                               "</td></tr>");
                    if (e.error_message) {
                        tr.addClass("danger");
                        tr.find("td.description").html(
                            $(" <strong>").text(e.error_message));
                        plugin_error = true;
                    }
                    tbody.append(tr);
                }
                if (plugin_error) {
                    popDialog("Some plugins failed to load. Please review " +
                              "any errors shown here and report them to an " +
                              "administrator as appropriate.");
                }
            }
        });
    };

    /**
     * Check whether the plugins are up-to-date and update the pluginTable.
     */
    function getAvailablePlugins() {
        $(c.anyPluginTable).find(".plugin-latest-cell").html("Checking&hellip;");
        let pb = startProgress($("#ys-progress"), "", "", "Checking plugins...");
        return $.ajax({
            url: "/api/yangsuite/plugins/avaliable",
            type: 'GET',
            datatype: 'json',
            success: function(retObj) {
                stopProgress(pb);

                for (let entry of retObj) {
                    let pkgName = entry['package_name'];
                    let tr = $(c.anyPluginTable).find('tr[data-value="' +
                                                      pkgName + '"]');
                    
                    /* If package is not ready to install due to 
                    response status from pypi,github
                    show the row as disabled radio input, 
                    blocking the possibility of installation */

                    let input = '<td><input type="radio" name="selection" id="'
                    
                    tr = $('<tr data-value="' + pkgName + '">' +
                            '<td><input type="radio"' + 
                            `name="selection" id="${entry.package_name}"></td>` +
                            '<td><code>' + entry.package_name + '</code></td>' +
                            '<td class="description" colspan="3">' +
                            entry.description + '</td>' + '</tr>');
                    $(c.availablePluginTable).append(tr);
                };
            }
        });
    };

    /**
     * Install a new plugin
     */
    async function installPlugin() {
        let selection = $(c.anyPluginTable).find("input:checked").toArray();
        if (selection.length == 0) {
            popDialog("No plugins selected");
            return;
        }
        let data = [];
        for (let input of selection) {
            data.push(input.getAttribute('id'));
        }
        await installUpdatePlugins(data);
    }


    /**
     * Update all installed plugins to their latest value
     */
    async function updatePlugins() {
        let developmentVersionInstalled = false;
        $(c.corePluginTable + ", " + c.extraPluginTable).find("tr").each(function() {
            let installedVersion = $(this).find(".plugin-installed-cell code").text();
            if (installedVersion.includes('dev')) {
                developmentVersionInstalled = true;
            }
        });

        if (developmentVersionInstalled) {
            if (!confirm("You have development/pre-release versions " +
                         "of some plugins installed. Continuing will replace " +
                         "these with the latest released versions. " +
                         "Continue anyway?")) {
                return;
            }
        }
        await installUpdatePlugins([]);
        await getSnapshots();
    }

    async function installPreRealeases(){
        let plugins = $(c.corePluginTable + ", " + c.extraPluginTable)
            .find(".plugin-latest-cell")
            .find("input:checked")
            .map(function(){return $(this).data("package")})
            .get();

        await installUpdatePlugins(plugins, true);
    }

    /**
     * Helper to installPlugin and updatePlugins()
     */
    async function installUpdatePlugins(data, pre_releases=false) {
        $("#ys-progress").progressbar({value: false});
        let p = jsonPromise("/api/yangsuite/plugins/update", 
                        {plugins: data, install_pre_releases: pre_releases});
        return $.when(p).then(function(retObj) {
            $("#ys-progress").progressbar("destroy");
            let list = $('<ul class="list-unstyled">');
            let anyUpdated = false;
            for (plugin of Object.keys(retObj.plugins)) {
                let result = retObj.plugins[plugin];
                if (result == 'updated') {
                    if (pre_releases){
                        list.append($("<li>" + plugin + " pre release version installed</li>"));
                    }
                    else{
                        list.append($("<li>" + plugin + " updated successfully</li>"));
                    }
                    anyUpdated = true;
                } else if (result == 'unchanged') {
                    if (pre_releases){
                        list.append($("<li>" + plugin + " has no pre release avaliable</li>"));
                    }
                    else{
                        list.append($("<li>" + plugin + " is up to date</li>"));
                    }
                } else {
                    list.append($("<li>" + plugin + " update result: " + result + "</li>"));
                }
            }
            let msg = $("<div>").text(retObj.message);
            msg.prepend(list);
            popDialog(msg);
            if (anyUpdated) {
                /*
                 * Server will restart after plugin update -
                 * give it a few seconds before we query it again
                 */
                setTimeout(function() { getInstalledPlugins() },
                           5000);
            }
        }, function() {
            /*
             * 'Failure' here probably means the server updated the plugin
             * successfully then restarted before sending our response.
             * Treat this as a successful update, and re-query after a few secs.
             */
            $("#ys-progress").progressbar("destroy");
            setTimeout(function() { getInstalledPlugins() }, 5000);
        });
    };

    async function getSnapshots(){
        let snapshotsSelect = $("#snapshots-select");
        $(snapshotsSelect).empty();
        $.ajax({
            url: "/api/yangsuite/plugins/snapshots",
            type: 'GET',
            datatype: 'json',
            success: function(retObj) {
                for (let timestamp of retObj.snapshots){
                    let snapshot = new Date(timestamp * 1000).toLocaleString()
                    $(snapshotsSelect).append(new Option(snapshot, timestamp))
                }
            }
        });
    }

    async function loadSnapshot(){
        $("#ys-progress").progressbar({value: false});
        // let snapshotsSelect = $("#snapshots-select");
        let p = jsonPromise(`/api/yangsuite/plugins/snapshots/`);
        return $.when(p).then(function(retObj) {
            $("#ys-progress").progressbar("destroy");
            popDialog(retObj.message);
        })
    }

    /* Public API */
    return {
        config:config,
        getInstalledPlugins:getInstalledPlugins,
        installPlugin:installPlugin,
        updatePlugins:updatePlugins,
        installPreRealeases: installPreRealeases,
        getAvailablePlugins: getAvailablePlugins,
        getSnapshots: getSnapshots,
        loadSnapshot: loadSnapshot,
    };
}();
