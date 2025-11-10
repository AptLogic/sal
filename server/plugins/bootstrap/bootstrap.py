from django.db.models import Q

import sal.plugin


TITLES = {
    'ok': 'Machines with Bootstrap supported and token escrowed',
    'not_supported': 'Machines without MDM Bootstrap support',
    'supported_not_escrowed': 'Machines with Bootstrap supported but token not escrowed',
    'unknown': 'Machines with unknown Bootstrap status'}
PLUGIN_Q = Q(pluginscriptsubmission__plugin='Bootstrap')
SCRIPT_Q = Q(pluginscriptsubmission__pluginscriptrow__pluginscript_name='Bootstrap')


class Bootstrap(sal.plugin.Widget):

    supported_os_families = [sal.plugin.OSFamilies.darwin]

    def get_context(self, queryset, **kwargs):
        queryset = queryset.filter(os_family='Darwin')
        context = self.super_get_context(queryset, **kwargs)
        context['ok'] = self._filter(queryset, 'ok').count()
        context['not_supported'] = self._filter(queryset, 'not_supported').count()
        context['supported_not_escrowed'] = self._filter(queryset, 'supported_not_escrowed').count()
        context['unknown'] = queryset.count() - context['ok'] - context['not_supported'] - context['supported_not_escrowed']
        return context

    def filter(self, machines, data):
        if data not in TITLES:
            return None, None
        return self._filter(machines, data), TITLES[data]

    def _filter(self, machines, data):
        machines = machines.filter(os_family='Darwin')
        if data == 'ok':
            machines = (
                machines
                .filter(PLUGIN_Q,
                        SCRIPT_Q,
                        pluginscriptsubmission__pluginscriptrow__pluginscript_data='Supported, Escrowed'))
        elif data == 'not_supported':
            machines = (
                machines
                .filter(PLUGIN_Q,
                        SCRIPT_Q,
                        pluginscriptsubmission__pluginscriptrow__pluginscript_data='Not Supported'))
        elif data == 'supported_not_escrowed':
            machines = (
                machines
                .filter(PLUGIN_Q,
                        SCRIPT_Q,
                        pluginscriptsubmission__pluginscriptrow__pluginscript_data='Supported, Not Escrowed'))
        elif data == 'unknown':
            machines = (
                machines
                .exclude(pk__in=self._filter(machines, 'ok').values('pk'))
                .exclude(pk__in=self._filter(machines, 'not_supported').values('pk'))
                .exclude(pk__in=self._filter(machines, 'supported_not_escrowed').values('pk')))

        return machines
