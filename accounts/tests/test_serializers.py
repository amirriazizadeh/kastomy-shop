from django.test import TestCase
from django.conf import settings
from django.test.utils import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import CustomUser
from accounts.serializers import UserProfileSerializer

from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import Address, CustomUser
from accounts.serializers import AddressSerializer, UserProfileSerializer
import tempfile
import tempfile
from io import BytesIO
from PIL import Image
from django.test import TestCase
from accounts.models import Address, CustomUser
from accounts.serializers import AddressSerializer
import tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import Address, CustomUser
from accounts.serializers import (AddressSerializer, OTPRequestSerializer, RegisterSerializer,
                                   UserProfileSerializer, UserSerializer, VerifyOTPSerializer)

class RegisterSerializerTest(TestCase):
    """تست‌های سریالایزر ثبت‌نام"""
    
    def setUp(self):
        """داده‌های اولیه"""
        self.valid_data = {
            'phone_number': '09123456789',
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
    
    def test_register_with_valid_data(self):
        """تست ثبت‌نام با داده‌های صحیح"""
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.phone_number, '09123456789')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('StrongPass123!'))
        self.assertEqual(user.role, CustomUser.Role.CUSTOMER)
    
    def test_password_mismatch(self):
        """تست عدم تطابق پسوردها"""
        data = self.valid_data.copy()
        data['password2'] = 'DifferentPass123!'
        
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_weak_password_validation(self):
        """تست پسوورد ضعیف"""
        data = self.valid_data.copy()
        data['password'] = '123'
        data['password2'] = '123'
        
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_duplicate_phone_number(self):
        """تست شماره تلفن تکراری"""
        CustomUser.objects.create_user(
            phone_number='09123456789',
            email='existing@example.com',
            password='pass123'
        )
        
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)
    
    def test_duplicate_email(self):
        """تست ایمیل تکراری"""
        CustomUser.objects.create_user(
            phone_number='09111111111',
            email='test@example.com',
            password='pass123'
        )
        
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_invalid_email_format(self):
        """تست فرمت نادرست ایمیل"""
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'
        
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_missing_required_fields(self):
        """تست فیلدهای الزامی"""
        required_fields = ['phone_number', 'email', 'password', 'password2']
        
        for field in required_fields:
            data = self.valid_data.copy()
            data.pop(field)
            
            serializer = RegisterSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)
    
    def test_password_not_in_response(self):
        """تست عدم نمایش پسوورد در خروجی"""
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        
        # پسوورد نباید در داده‌های سریالایز شده باشد
        self.assertNotIn('password', serializer.data)
        self.assertNotIn('password2', serializer.data)


class UserSerializerTest(TestCase):
    """تست‌های سریالایزر نمایش کاربر"""
    
    def setUp(self):
        """ساخت یوزر تست"""
        self.user = CustomUser.objects.create_user(
            phone_number='09123456789',
            email='test@example.com',
            password='pass123'
        )
    
    def test_user_serialization(self):
        """تست سریالایز کردن کاربر"""
        serializer = UserSerializer(self.user)
        
        self.assertEqual(serializer.data['phone_number'], '09123456789')
        self.assertEqual(serializer.data['email'], 'test@example.com')
        self.assertEqual(serializer.data['role'], CustomUser.Role.CUSTOMER)
        self.assertIn('id', serializer.data)
    
    def test_password_not_exposed(self):
        """تست عدم نمایش پسوورد"""
        serializer = UserSerializer(self.user)
        self.assertNotIn('password', serializer.data)


class OTPRequestSerializerTest(TestCase):
    """تست‌های سریالایزر درخواست OTP"""
    
    def test_valid_phone_number(self):
        """تست شماره تلفن معتبر"""
        data = {'phone_number': '09123456789'}
        serializer = OTPRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_missing_phone_number(self):
        """تست عدم ارسال شماره تلفن"""
        serializer = OTPRequestSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)


class VerifyOTPSerializerTest(TestCase):
    """تست‌های سریالایزر تایید OTP"""
    
    def test_valid_otp_data(self):
        """تست داده‌های معتبر OTP"""
        data = {
            'phone_number': '09123456789',
            'otp': '123456'
        }
        serializer = VerifyOTPSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_missing_fields(self):
        """تست فیلدهای ناقص"""
        # بدون OTP
        serializer = VerifyOTPSerializer(data={'phone_number': '09123456789'})
        self.assertFalse(serializer.is_valid())
        
        # بدون شماره تلفن
        serializer = VerifyOTPSerializer(data={'otp': '123456'})
        self.assertFalse(serializer.is_valid())
    
    def test_otp_write_only(self):
        """تست write_only بودن OTP"""
        data = {
            'phone_number': '09123456789',
            'otp': '123456'
        }
        serializer = VerifyOTPSerializer(data={'phone_number': '09123456789', 'otp': '1234'})
        serializer.is_valid()
    
        # otp باید در خروجی serializer.data وجود نداشته باشه
        self.assertNotIn('otp', serializer.data.keys())







class UserProfileSerializerTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            phone_number='09123456789',
            email='test@example.com',
            password='pass123'
        )

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_profile_picture_upload(self):
        # یک بافر در حافظه ایجاد کنید
        image_buffer = BytesIO()
        # یک تصویر واقعی با Pillow ایجاد کنید و در بافر ذخیره کنید
        image = Image.new('RGB', size=(1, 1), color=(255, 0, 0))
        image.save(image_buffer, format='PNG')
        image_buffer.seek(0)  # بازگرداندن نشانگر فایل به ابتدای بافر

        # یک SimpleUploadedFile معتبر از بافر ایجاد کنید
        uploaded_image = SimpleUploadedFile(
            name='test_profile_picture.png',
            content=image_buffer.getvalue(),
            content_type='image/png'
        )

        data = {'profile_picture': uploaded_image}
        serializer = UserProfileSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_user = serializer.save()
        
        # بررسی کنید که تصویر با موفقیت ذخیره شده است
        self.assertTrue(updated_user.profile_picture)
        


# -------------------------
# تست‌های AddressSerializer
# -------------------------
class AddressSerializerTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            phone_number='09123456789',
            email='test@example.com',
            password='pass123'
        )
        # داده‌های معتبر برای serializer
        self.address_data = {
            'user': self.user,  # instance واقعی
            'label': 'خانه',
            'address_line_1': 'خیابان ولیعصر',
            'address_line_2': 'پلاک ۱۰',
            'city': 'تهران',
            'state': 'تهران',
            'postal_code': '1234567890',
            'country': 'ایران',
            'is_main': True
        }

    def test_address_creation_via_serializer(self):
        """تست ساخت آدرس از طریق serializer"""
        serializer = AddressSerializer(data=self.address_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        address = serializer.save(user=self.user)  # با متد create اصلاح‌شده
        self.assertEqual(address.label, 'خانه')
        self.assertEqual(address.address_line_1, 'خیابان ولیعصر')
        self.assertEqual(address.city, 'تهران')
        self.assertEqual(address.postal_code, '1234567890')
        self.assertEqual(address.user, self.user)

    def test_user_and_id_are_read_only(self):
        """تست read_only بودن فیلدهای id و user"""
        address = Address.objects.create(**self.address_data)

        serializer = AddressSerializer(address)
        data = serializer.data

        # بررسی اینکه فیلدهای read_only در خروجی هستند
        self.assertIn('id', data)
        self.assertIn('user', data)

        # بررسی اینکه نمی‌توان آنها را آپدیت کرد
        update_data = {
            'id': 9999,
            'user': None,
            'label': 'محل کار'
        }
        serializer = AddressSerializer(address, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_address = serializer.save()

        # id و user نباید تغییر کنند
        self.assertEqual(updated_address.id, address.id)
        self.assertEqual(updated_address.user, self.user)
        # سایر فیلدها می‌توانند تغییر کنند
        self.assertEqual(updated_address.label, 'محل کار')

