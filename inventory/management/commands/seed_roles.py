from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from inventory.models import Product, Order, Delivery, Issue


def perms_for_model(model, actions):
    ct = ContentType.objects.get_for_model(model)
    codenames = [f'{action}_{model._meta.model_name}' for action in actions]
    return list(Permission.objects.filter(content_type=ct, codename__in=codenames))


class Command(BaseCommand):
    help = 'Creates Marketing Team and Storekeeper groups with suitable permissions.'

    def handle(self, *args, **options):
        marketing, _ = Group.objects.get_or_create(name='Marketing Team')
        storekeeper, _ = Group.objects.get_or_create(name='Storekeeper')

        marketing_permissions = []
        for model in [Product, Order, Delivery, Issue]:
            marketing_permissions.extend(perms_for_model(model, ['add', 'change', 'delete', 'view']))

        storekeeper_permissions = []
        for model in [Product, Order, Delivery, Issue]:
            storekeeper_permissions.extend(perms_for_model(model, ['view']))
        storekeeper_permissions.extend(perms_for_model(Issue, ['add', 'change']))

        marketing.permissions.set(marketing_permissions)
        storekeeper.permissions.set(storekeeper_permissions)

        self.stdout.write(self.style.SUCCESS('Groups created/updated: Marketing Team, Storekeeper'))
