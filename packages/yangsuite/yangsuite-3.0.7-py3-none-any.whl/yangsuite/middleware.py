# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

from asgiref.sync import iscoroutinefunction, sync_to_async
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import sync_and_async_middleware
from whitenoise.middleware import WhiteNoiseMiddleware

from yangsuite.apps import FAILED_APPS


@sync_and_async_middleware
def send_to_plugins_once_if_plugin_errors(get_response):
    # One-time configuration and initialization would go here

    async def async_middleware(request):
        is_authenticated = await sync_to_async(
            lambda request: request.user.is_authenticated
        )(request)
        if is_authenticated and FAILED_APPS:
            if not request.session.get("already_reported_plugin_errors", False):
                request.session["already_reported_plugin_errors"] = True
                return HttpResponseRedirect(reverse("plugins"))
        response = await get_response(request)
        if not FAILED_APPS:
            if "already_reported_plugin_errors" in request.session:
                del request.session["already_reported_plugin_errors"]
        return response

    def middleware(request):
        # Execute this code before the view or any later middleware are called
        if request.user.is_authenticated and FAILED_APPS:
            if not request.session.get("already_reported_plugin_errors", False):
                request.session["already_reported_plugin_errors"] = True
                return HttpResponseRedirect(reverse("plugins"))

        # Pass it on
        response = get_response(request)

        # Anything to do after the view has been called
        if not FAILED_APPS:
            if "already_reported_plugin_errors" in request.session:
                del request.session["already_reported_plugin_errors"]

        # Done
        return response

    if iscoroutinefunction(get_response):
        return async_middleware
    else:
        return middleware


@sync_and_async_middleware
def whitenoise_middleware(get_response):
    mid = WhiteNoiseMiddleware(get_response)

    def get_static_file(request):
        # This logic is copied from WhiteNoiseMiddleware.__call__
        if mid.autorefresh:
            static_file = mid.find_file(request.path_info)
        else:
            static_file = mid.files.get(request.path_info)
        return mid.serve(static_file, request) if static_file is not None else None

    if iscoroutinefunction(get_response):
        aget_static_file = sync_to_async(get_static_file, thread_sensitive=False)

        async def middleware(request):
            response = await aget_static_file(request)
            if response is not None:
                return response

            return await get_response(request)

    else:

        def middleware(request):
            response = get_static_file(request)
            if response is not None:
                return response

            return get_response(request)

    return middleware
