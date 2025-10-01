from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class UserManagerTestCase(TestCase):
    """تست‌های مربوط به UserManager"""

    def test_create_user_successful(self):
        """تست ایجاد کاربر عادی با موفقیت"""
        user = User.objects.create_user(
            phone_number='09123456789',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.phone_number, '09123456789')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.role, User.Role.CUSTOMER)

    def test_create_user_without_phone_number(self):
        """تست ایجاد کاربر بدون شماره تلفن - باید خطا دهد"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                phone_number='',
                email='test@example.com',
                password='testpass123'
            )
        self.assertEqual(str(context.exception), 'The Phone Number field must be set')

    def test_create_user_without_email(self):
        """تست ایجاد کاربر بدون ایمیل - باید خطا دهد"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                phone_number='09123456789',
                email='',
                password='testpass123'
            )
        self.assertEqual(str(context.exception), 'The Email field must be set')

    def test_create_superuser_successful(self):
        """تست ایجاد ادمین با موفقیت"""
        admin = User.objects.create_superuser(
            phone_number='09123456789',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)
        self.assertEqual(admin.role, User.Role.ADMIN)

    def test_create_superuser_with_is_staff_false(self):
        """تست ایجاد ادمین با is_staff=False - باید خطا دهد"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                phone_number='09123456789',
                email='admin@example.com',
                password='adminpass123',
                is_staff=False
            )
        self.assertEqual(str(context.exception), 'Superuser must have is_staff=True.')


# ///////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////


class CustomUserModelTestCase(TestCase):
    """تست‌های مربوط به مدل CustomUser"""

    def setUp(self):
        """ایجاد داده‌های اولیه برای تست‌ها"""
        self.user_data = {
            'phone_number': '09123456789',
            'email': 'test@example.com',
            'password': 'testpass123'
        }

    def test_user_creation_with_valid_data(self):
        """تست ایجاد کاربر با داده‌های صحیح"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.phone_number, self.user_data['phone_number'])

    def test_phone_number_validation_invalid_format(self):
        """تست اعتبارسنجی شماره تلفن با فرمت نادرست"""
        user = User(
            phone_number='12345',
            email='test@example.com'
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_phone_number_validation_valid_format(self):
        """تست اعتبارسنجی شماره تلفن با فرمت صحیح"""
        user = User(
            phone_number='09123456789',
            password='strongpassword1234@',
            email='test1@example.com'
        )
        user.full_clean() 
        self.assertTrue(True)

    def test_unique_phone_number(self):
        """تست یکتا بودن شماره تلفن"""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                phone_number='09123456789',
                email='another@example.com',
                password='pass123'
            )

    def test_unique_email(self):
        """تست یکتا بودن ایمیل"""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                phone_number='09987654321',
                email='test@example.com',
                password='pass123'
            )

    def test_user_str_method(self):
        """تست متد __str__ کاربر"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), '09123456789')

    def test_default_role_is_customer(self):
        """تست نقش پیش‌فرض کاربر (مشتری)"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.role, User.Role.CUSTOMER)

    def test_default_is_active_false(self):
        """تست وضعیت پیش‌فرض فعال بودن (غیرفعال)"""
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_active)


# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////


class AddressModelTestCase(TestCase):
    """تست‌های مربوط به مدل Address"""

    def setUp(self):
        """ایجاد کاربر برای تست‌های آدرس"""
        self.user = User.objects.create_user(
            phone_number='09123456789',
            email='test@example.com',
            password='testpass123'
        )
        self.address_data = {
            'user': self.user,
            'label': 'خانه',
            'address_line_1': 'خیابان آزادی',
            'city': 'تهران',
            'state': 'تهران',
            'postal_code': '1234567890',
            'country': 'ایران'
        }

    def test_create_address_successful(self):
        """تست ایجاد آدرس با موفقیت"""
        from accounts.models import Address  
        address = Address.objects.create(**self.address_data)
        self.assertEqual(Address.objects.count(), 1)
        self.assertEqual(address.label, 'خانه')
        self.assertTrue(address.is_main)  

    def test_first_address_becomes_main(self):
        """تست اینکه اولین آدرس به صورت خودکار اصلی می‌شود"""
        from accounts.models import Address
        address = Address.objects.create(**self.address_data)
        self.assertTrue(address.is_main)

    def test_second_address_makes_first_not_main(self):
        """تست اینکه آدرس جدید، آدرس قبلی را غیراصلی می‌کند"""
        from accounts.models import Address
        address1 = Address.objects.create(**self.address_data)
        
        address2_data = self.address_data.copy()
        address2_data['label'] = 'محل کار'
        address2_data['postal_code'] = '0987654321'
        address2 = Address.objects.create(**address2_data)
        
        address1.refresh_from_db()
        self.assertFalse(address1.is_main)
        self.assertTrue(address2.is_main)

    def test_unique_postal_code(self):
        """تست یکتا بودن کد پستی"""
        from accounts.models import Address
        Address.objects.create(**self.address_data)
        
        duplicate_data = self.address_data.copy()
        duplicate_data['label'] = 'محل کار'
        
        with self.assertRaises(IntegrityError):
            Address.objects.create(**duplicate_data)

    def test_address_str_method(self):
        """تست متد __str__ آدرس"""
        from accounts.models import Address
        self.user.first_name = 'علی'
        self.user.save()
        address = Address.objects.create(**self.address_data)
        self.assertEqual(str(address), 'خانه - علی')



# ///////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////



class RegisterViewTestCase(APITestCase):
    """تست‌های مربوط به API ثبت‌نام"""

    def setUp(self):
        """تنظیمات اولیه برای تست‌های API"""
        self.register_url = reverse('register')  
        self.valid_data = {
            'phone_number': '09123456789',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!'
        }

    def test_register_user_successful(self):
        """تست ثبت‌نام موفق کاربر"""
        response = self.client.post(self.register_url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(User.objects.count(), 1)
        
        user = User.objects.first()
        self.assertEqual(user.phone_number, self.valid_data['phone_number'])
        self.assertEqual(user.email, self.valid_data['email'])

    def test_register_with_mismatched_passwords(self):
        """تست ثبت‌نام با عدم تطابق رمزهای عبور"""
        invalid_data = self.valid_data.copy()
        invalid_data['password2'] = 'DifferentPass123!'
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_register_with_existing_phone_number(self):
        """تست ثبت‌نام با شماره تلفن تکراری"""
        User.objects.create_user(**{
            'phone_number': '09123456789',
            'email': 'existing@example.com',
            'password': 'pass123'
        })
        
        response = self.client.post(self.register_url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_register_with_existing_email(self):
        """تست ثبت‌نام با ایمیل تکراری"""
        User.objects.create_user(**{
            'phone_number': '09987654321',
            'email': 'test@example.com',
            'password': 'pass123'
        })
        
        response = self.client.post(self.register_url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_register_with_invalid_phone_format(self):
        """تست ثبت‌نام با فرمت نادرست شماره تلفن"""
        invalid_data = self.valid_data.copy()
        invalid_data['phone_number'] = '12345'
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_register_with_missing_required_fields(self):
        """تست ثبت‌نام با فیلدهای ضروری خالی"""
        response = self.client.post(self.register_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_register_allows_unauthenticated_access(self):
        """تست اینکه API ثبت‌نام برای کاربران احراز هویت نشده در دسترس است"""
        response = self.client.post(self.register_url, self.valid_data, format='json')
        # نباید خطای 401 یا 403 دریافت کنیم
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)