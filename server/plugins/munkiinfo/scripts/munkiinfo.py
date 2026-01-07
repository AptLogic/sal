#!/usr/local/sal/Python.framework/Versions/Current/bin/python3

import sys
import sal
from Foundation import CFPreferencesCopyAppValue
from Foundation import CFPreferencesAppSynchronize
from Foundation import kCFPreferencesCurrentHost
from Foundation import kCFPreferencesAnyUser
from Foundation import CFPreferencesSetValue
from Foundation import NSDate

BUNDLE_ID = 'ManagedInstalls'

PREFS_TO_GET = (
    'ManagedInstallDir',
    'SoftwareRepoURL',
    'ClientIdentifier',
    'LogFile',
    'LoggingLevel',
    'LogToSyslog',
    'InstallAppleSoftwareUpdates',
    'AppleSoftwareUpdatesOnly',
    'SoftwareUpdateServerURL',
    'DaysBetweenNotifications',
    'LastNotifiedDate',
    'UseClientCertificate',
    'SuppressUserNotification',
    'SuppressAutoInstall',
    'SuppressStopButtonOnInstall',
    'PackageVerificationMode',
    'FollowHTTPRedirects',
    'UnattendedAppleUpdates',
    'ClientCertificatePath',
    'ClientKeyPath',
    'LastAppleSoftwareUpdateCheck',
    'LastCheckDate',
    'LastCheckResult',
    'LogFile',
    'SoftwareRepoCACertificate',
    'SoftwareRepoCAPath',
    'PackageURL',
    'CatalogURL',
    'ManifestURL',
    'IconURL',
    'ClientResourceURL',
    'ClientResourcesFilename',
    'HelpURL',
    'UseClientCertificateCNAsClientIdentifier',
    'AdditionalHttpHeaders',
    'SuppressLoginwindowInstall',
    'InstallRequiresLogout',
    'ShowRemovalDetail',
    'MSULogEnabled',
    'MSUDebugLogEnabled',
    'LocalOnlyManifest',
    'UnattendedAppleUpdates')

DEFAULT_PREFS = {
    'AdditionalHttpHeaders': None,
    'AggressiveUpdateNotificationDays': 14,
    'AppleSoftwareUpdatesIncludeMajorOSUpdates': False,
    'AppleSoftwareUpdatesOnly': False,
    'CatalogURL': None,
    'ClientCertificatePath': None,
    'ClientIdentifier': '',
    'ClientKeyPath': None,
    'ClientResourcesFilename': None,
    'ClientResourceURL': None,
    'DaysBetweenNotifications': 1,
    'EmulateProfileSupport': False,
    'FollowHTTPRedirects': 'none',
    'HelpURL': None,
    'IconURL': None,
    'IgnoreMiddleware': False,
    'IgnoreSystemProxies': False,
    'InstallRequiresLogout': False,
    'InstallAppleSoftwareUpdates': False,
    'LastNotifiedDate': NSDate.dateWithTimeIntervalSince1970_(0),
    'LocalOnlyManifest': None,
    'LogFile': '/Library/Managed Installs/Logs/ManagedSoftwareUpdate.log',
    'LoggingLevel': 1,
    'LogToSyslog': False,
    'ManagedInstallDir': '/Library/Managed Installs',
    'ManifestURL': None,
    'PackageURL': None,
    'PackageVerificationMode': 'hash',
    'PerformAuthRestarts': False,
    'RecoveryKeyFile': None,
    'ShowOptionalInstallsForHigherOSVersions': False,
    'SoftwareRepoCACertificate': None,
    'SoftwareRepoCAPath': None,
    'SoftwareRepoURL': 'http://munki/repo',
    'SoftwareUpdateServerURL': None,
    'SuppressAutoInstall': False,
    'SuppressLoginwindowInstall': False,
    'SuppressStopButtonOnInstall': False,
    'SuppressUserNotification': False,
    'UnattendedAppleUpdates': False,
    'UseClientCertificate': False,
    'UseClientCertificateCNAsClientIdentifier': False,
    'UseNotificationCenterDays': 3,
}

def main():
    # Skip a manual check
    if len(sys.argv) > 1:
        if sys.argv[1] == 'manualcheck':
            # Manual check: skipping MunkiInfo Plugin
            exit(0)

    data = {pref: str(munkiGetPref(pref)) for pref in PREFS_TO_GET}
    sal.add_plugin_results('MunkiInfo', data)

def munkiGetPref(pref_name):
    """Return a preference. Since this uses CFPreferencesCopyAppValue,
    Preferences can be defined several places. Precedence is:
        - MCX/configuration profile
        - /var/root/Library/Preferences/ByHost/ManagedInstalls.XXXXXX.plist
        - /var/root/Library/Preferences/ManagedInstalls.plist
        - /Library/Preferences/ManagedInstalls.plist
        - .GlobalPreferences defined at various levels (ByHost, user, system)
        - default_prefs defined here.
    """
    pref_value = CFPreferencesCopyAppValue(pref_name, BUNDLE_ID)
    if pref_value is None:
        pref_value = DEFAULT_PREFS.get(pref_name)
        # we're using a default value. We'll write it out to
        # /Library/Preferences/<BUNDLE_ID>.plist for admin
        # discoverability
        if pref_value is not None:
            set_pref(pref_name, pref_value)
    if isinstance(pref_value, NSDate):
        # convert NSDate/CFDates to strings
        pref_value = str(pref_value)
    return pref_value


def set_pref(pref_name, pref_value):
    """Sets a preference, writing it to
    /Library/Preferences/ManagedInstalls.plist.
    This should normally be used only for 'bookkeeping' values;
    values that control the behavior of munki may be overridden
    elsewhere (by MCX, for example)"""
    try:
        CFPreferencesSetValue(
            pref_name, pref_value, BUNDLE_ID,
            kCFPreferencesAnyUser, kCFPreferencesCurrentHost)
        CFPreferencesAppSynchronize(BUNDLE_ID)
    except BaseException:
        pass


if __name__ == '__main__':
    main()
