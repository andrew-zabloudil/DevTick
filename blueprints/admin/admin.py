from flask import redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


class AdminIndexView(AdminIndexView):
    # Creates Admin model views
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.id == 1
        else:
            return False

    # Redirects user to login page
    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('auth.login'))


class DevTickModelView(ModelView):

    column_exclude_list = ('password')
    column_display_pk = True
    # Makes the admin view only accessible by the user with id of 0

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.id == 1
        else:
            return False

    # Redirects user to login page
    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('auth.login'))
