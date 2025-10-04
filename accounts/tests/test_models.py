
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from accounts.models import CustomUser


class CustomUserModelTest(TestCase):
    """تست‌های مدل CustomUser"""
    
    def setUp(self):
        """داده‌های اولیه برای تست‌ها"""
        self.user_data = {
            'phone_number': '09123456789',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    
    def test_create_user_with_valid_data(self):
        """تست ساخت یوزر با داده‌های صحیح"""
        user = CustomUser.objects.create_user(**self.user_data)
        
        self.assertEqual(user.phone_number, '09123456789')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.role, CustomUser.Role.CUSTOMER)
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_seller)
    
    def test_create_superuser(self):
        """تست ساخت سوپریوزر"""
        admin = CustomUser.objects.create_superuser(
            phone_number='09111111111',
            email='admin@example.com',
            password='admin123'
        )
        
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)
    
    def test_phone_number_is_unique(self):
        """تست یونیک بودن شماره تلفن"""
        CustomUser.objects.create_user(**self.user_data)
        
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                phone_number='09123456789',
                email='another@example.com',
                password='pass123'
            )
    
    def test_email_is_unique(self):
        """تست یونیک بودن ایمیل"""
        CustomUser.objects.create_user(**self.user_data)
        
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                phone_number='09111111111',
                email='test@example.com',
                password='pass123'
            )
    
    def test_invalid_phone_number_format(self):
        """تست فرمت نادرست شماره تلفن"""
        invalid_phones = [
            '9123456789',      # بدون صفر
            '091234567',       # کمتر از 11 رقم
            '091234567890',    # بیشتر از 11 رقم
            '08123456789',     # شروع با 08
            'abcd1234567',     # حروف
        ]
        
        for phone in invalid_phones:
            user = CustomUser(
                phone_number=phone,
                email=f'{phone}@test.com',
                password='pass123'
            )
            with self.assertRaises(ValidationError):
                user.full_clean()
    
    def test_valid_phone_number_format(self):
        """تست فرمت صحیح شماره تلفن"""
        valid_phones = [
            '09123456789',
            '09991234567',
            '09011111111',
        ]
        
        for i, phone in enumerate(valid_phones):
            user = CustomUser(
                phone_number=phone,
                email=f'test{i}@example.com',
                password='pass123'
            )
            user.full_clean()  # نباید خطا بدهد
            user.save()
            self.assertEqual(user.phone_number, phone)
    
    def test_user_str_method(self):
        """تست متد __str__"""
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(str(user), '09123456789')
    
    def test_default_role_is_customer(self):
        """تست نقش پیش‌فرض کاربر"""
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.role, CustomUser.Role.CUSTOMER)
    
    def test_role_choices(self):
        """تست انتخاب‌های مختلف نقش"""
        roles = [
            CustomUser.Role.CUSTOMER,
            CustomUser.Role.SELLER,
            CustomUser.Role.ADMIN
        ]
        
        for i, role in enumerate(roles):
            user = CustomUser.objects.create_user(
                phone_number=f'0912345678{i}',
                email=f'user{i}@example.com',
                password='pass123',
                role=role
            )
            self.assertEqual(user.role, role)
    
    def test_optional_fields(self):
        """تست فیلدهای اختیاری"""
        user = CustomUser.objects.create_user(
            **self.user_data,
            first_name='علی',
            last_name='احمدی',
            is_seller=True
        )
        
        self.assertEqual(user.first_name, 'علی')
        self.assertEqual(user.last_name, 'احمدی')
        self.assertTrue(user.is_seller)
    
    def test_username_field_is_phone_number(self):
        """تست USERNAME_FIELD"""
        self.assertEqual(CustomUser.USERNAME_FIELD, 'phone_number')
    
    def test_required_fields(self):
        """تست فیلدهای الزامی"""
        self.assertIn('email', CustomUser.REQUIRED_FIELDS)
    
    def test_create_user_without_phone_number(self):
        """تست ساخت یوزر بدون شماره تلفن"""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                phone_number='',
                email='test@example.com',
                password='pass123'
            )
    
    def test_create_user_without_email(self):
        """تست ساخت یوزر بدون ایمیل"""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                phone_number='09123456789',
                email='',
                password='pass123'
            )
    
    def test_user_permissions(self):
        """تست سیستم پرمیشن‌ها"""
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertFalse(user.has_perm('any_permission'))
        
        # سوپریوزر همه پرمیشن‌ها رو داره
        admin = CustomUser.objects.create_superuser(
            phone_number='09111111111',
            email='admin@example.com',
            password='admin123'
        )
        self.assertTrue(admin.has_perm('any_permission'))
    
    def test_profile_picture_upload(self):
        """تست آپلود عکس پروفایل"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )
        
        user = CustomUser.objects.create_user(
            **self.user_data,
            profile_picture=image
        )
        
        self.assertTrue(user.profile_picture)
        self.assertIn('profiles/', user.profile_picture.name)