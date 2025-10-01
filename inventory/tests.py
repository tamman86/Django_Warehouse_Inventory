from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User, Group, Permission
from .models import Status, Pump, Valve, LogEntry, RepairLog, BaseItem


class StatusModelTest(TestCase):

    # Test if status is created properly
    def test_can_create_status(self):
        # Create a new Status object in the test database
        status = Status.objects.create(name="On Loan")

        # Check there is a status in the database
        self.assertEqual(Status.objects.count(), 1)

        # Check the name is correct
        retrieved_status = Status.objects.first()
        self.assertEqual(retrieved_status.name, "On Loan")

class PumpModelTest(TestCase):

    def setUp(self):
        """
        This special method runs before every test in this class.
        We use it to set up objects that multiple tests might need.
        """
        self.warehouse_status = Status.objects.create(name="Warehouse")
        self.repair_status = Status.objects.create(name="Repair")

    def test_pump_creation_creates_log_entry(self):
        """
        Tests that creating a new Pump item automatically triggers a 'Created' log entry.
        """
        # Act: Create a new Pump item
        pump = Pump.objects.create(
            item_id="P-101",
            category="Pump",
            description="Test Water Pump",
            status=self.warehouse_status
        )

        # Assert: Check that a LogEntry was created correctly
        self.assertEqual(LogEntry.objects.count(), 1)
        log = LogEntry.objects.first()
        self.assertEqual(log.action, "Created")
        self.assertEqual(log.item_id_str, "P-101")

    def test_repair_lifecycle(self):

        # Create a pump to be repaired
        pump = Pump.objects.create(
            item_id="P-101",
            category="Pump",
            status=self.repair_status  # Create the pump in "repair" status
        )

        # Create a new, active repair log for the pump
        repair_log = RepairLog.objects.create(
            item=pump,
            repair_company="Test Repair Co",
            start_date=timezone.now().date(),
            description="Leaking seal"
        )

        # Check that the repair is active
        self.assertEqual(pump.repairs.count(), 1)
        self.assertTrue(repair_log.is_active)

        # Simulate completing the repair
        repair_log.is_active = False
        repair_log.end_date = timezone.now().date()
        repair_log.save()

        pump.status = self.warehouse_status
        pump.save()

        # Check that the repair is now complete and the item's status is updated
        reloaded_pump = Pump.objects.get(pk=pump.pk)
        self.assertEqual(reloaded_pump.status.name, "Warehouse")

        reloaded_repair = reloaded_pump.repairs.first()
        self.assertFalse(reloaded_repair.is_active)
        self.assertIsNotNone(reloaded_repair.end_date)

class InventoryViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.warehouse_status = Status.objects.create(name="Warehouse")

        # Create a "Viewer" group with only the permission to view items
        self.viewer_group = Group.objects.create(name='Viewer')
        can_view_item = Permission.objects.get(codename='view_baseitem')
        self.viewer_group.permissions.add(can_view_item)
        self.viewer_user = User.objects.create_user(username='viewer', password='password123')
        self.viewer_user.groups.add(self.viewer_group)

        self.manager_group = Group.objects.create(name='Warehouse Manager')
        add_perm = Permission.objects.get(codename='add_baseitem')
        change_perm = Permission.objects.get(codename='change_baseitem')
        delete_perm = Permission.objects.get(codename='delete_baseitem')
        self.manager_group.permissions.add(add_perm, change_perm, delete_perm)
        self.manager_user = User.objects.create_user(username='manager', password='password123')
        self.manager_user.groups.add(self.manager_group)

        # Create an item that we can try to delete
        self.item_to_delete = BaseItem.objects.create(item_id='TEST-001', category='Misc')

    def test_add_item_page_redirects_when_logged_out(self):
        # Get the URL for a protected page
        add_page_url = reverse('add_item_chooser')

        # Use the client to "visit" the page
        response = self.client.get(add_page_url)

        # Check that the response is a redirect (status code 302)
        self.assertEqual(response.status_code, 302)

        # Check that the redirect location is the login page
        login_page_url = reverse('login')
        self.assertRedirects(response, f'{login_page_url}?next={add_page_url}')

    def test_delete_item_is_forbidden_for_viewer(self):
        # Log in our test "viewer" user
        self.client.login(username='viewer', password='password123')

        # Get the URL for the delete page of our test item
        delete_url = reverse('delete_item', kwargs={'pk': self.item_to_delete.pk})

        # Use the logged-in client to visit the delete page
        response = self.client.get(delete_url)

        # Check that the response is a 403 Forbidden error
        self.assertEqual(response.status_code, 403)

    def test_manager_can_add_new_item(self):
        self.client.login(username='manager', password='password123')

        # Create Item
        form_data = {
            'item_id': 'V-500',
            'description': 'Test Gate Valve',
            'vendor': 'Test Vendor',
            'status': self.warehouse_status.id
        }

        # POST the data to the add_item URL for the 'Valve' category
        response = self.client.post(reverse('add_item', kwargs={'category': 'Valve'}), data=form_data)

        # Check that a new Valve was actually created in the database
        self.assertEqual(Valve.objects.count(), 1)
        new_valve = Valve.objects.first()
        self.assertEqual(new_valve.item_id, 'V-500')

        # Check that the user was redirected back to the main item list
        self.assertRedirects(response, reverse('item_list'))

    def test_add_item_with_invalid_data(self):
        # Log in the manager user
        self.client.login(username='manager', password='password123')

        # This data is invalid because it's missing the required 'item_id' field
        invalid_form_data = {
            'description': 'A valve with no ID',
            'vendor': 'Test Vendor',
            'status': self.warehouse_status.id
        }

        # POST the invalid data
        response = self.client.post(reverse('add_item', kwargs={'category': 'Valve'}), data=invalid_form_data)

        # Check that NO new Valve was created in the database
        self.assertEqual(Valve.objects.count(), 0)

        # Check that the page re-rendered (status code 200) instead of redirecting
        self.assertEqual(response.status_code, 200)

        # Check that the page HTML contains the expected error message
        self.assertContains(response, "This field is required.")