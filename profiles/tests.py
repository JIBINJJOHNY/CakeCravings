from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile
from django_countries.fields import Country
from datetime import date

class ProfileModelTest(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create(username='testuser')

    def test_profile_creation(self):
        # Create a profile and check if it's saved successfully
        profile = Profile.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            birthday=date(1990, 1, 1),
            phone_number='123456789',
            country=Country('US'),
            postcode='12345',
            town_or_city='Test City',
            street_address1='123 Test St',
            street_address2='Apt 4',
            county='Test County',
        )

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.first_name, 'John')
        self.assertEqual(profile.last_name, 'Doe')
        self.assertEqual(profile.birthday, date(1990, 1, 1))
        self.assertEqual(profile.phone_number, '123456789')
        self.assertEqual(profile.country, Country('US'))
        self.assertEqual(profile.postcode, '12345')
        self.assertEqual(profile.town_or_city, 'Test City')
        self.assertEqual(profile.street_address1, '123 Test St')
        self.assertEqual(profile.street_address2, 'Apt 4')
        self.assertEqual(profile.county, 'Test County')

    def test_profile_str_method(self):
        # Test the __str__ method of the Profile model
        profile = Profile.objects.create(user=self.user, first_name='John', last_name='Doe')

        self.assertEqual(str(profile), 'John Doe')

    def test_profile_age_property(self):
        # Test the age property of the Profile model
        profile = Profile.objects.create(user=self.user, birthday=date(1990, 1, 1))

        self.assertEqual(profile.age, 33)  # Assuming the current year is 2023

    def test_profile_age_property_invalid_birthday(self):
        # Test the age property with an invalid birthday
        profile = Profile.objects.create(user=self.user, birthday=date(2090, 1, 1))

        self.assertEqual(profile.age, 'Invalid birthday')

    def test_profile_age_property_no_birthday(self):
        # Test the age property with no birthday
        profile = Profile.objects.create(user=self.user)

        self.assertIsNone(profile.age)
