from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy


class PermissionRequired(LoginRequiredMixin, PermissionRequiredMixin):

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(f'/account/login/?next={self.request.path}')
        else:
            messages.error(self.request, 'شما دسترسی لازم رو ندارید!')
        return redirect('Home:Index')

