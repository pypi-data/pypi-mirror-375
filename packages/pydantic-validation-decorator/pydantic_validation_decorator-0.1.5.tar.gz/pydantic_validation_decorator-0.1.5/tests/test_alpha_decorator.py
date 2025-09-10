import pytest
from pydantic_validation_decorator import (
    ValidateFields,
    Alpha,
    FieldValidationError,
)
from pydantic import BaseModel
from typing import Optional


class AlphaTestModel(BaseModel):
    username: Optional[str] = None
    upper_name: Optional[str] = None
    lower_name: Optional[str] = None
    mixed_name: Optional[str] = None

    @Alpha(
        field_name='username',
        mode='mixed',
        message='用户名必须只包含字母',
    )
    def get_username(self):
        return self.username

    @Alpha(
        field_name='upper_name',
        mode='upper',
        message='名称必须只包含大写字母',
    )
    def get_upper_name(self):
        return self.upper_name

    @Alpha(
        field_name='lower_name',
        mode='lower',
        message='名称必须只包含小写字母',
    )
    def get_lower_name(self):
        return self.lower_name

    @Alpha(
        field_name='mixed_name',
        mode='mixed',
    )
    def get_mixed_name(self):
        return self.mixed_name

    def validate_fields(self):
        self.get_username()
        self.get_upper_name()
        self.get_lower_name()
        self.get_mixed_name()


@ValidateFields(validate_model='alpha_test', validate_function='get_username')
def sync_test_alpha_decorator(alpha_test: AlphaTestModel):
    return alpha_test.model_dump()


@ValidateFields(mode='args', validate_model_index=1)
async def async_test_alpha_decorator(test, alpha_test):
    return alpha_test.model_dump()


class TestAlphaDecorator:
    """测试 Alpha 装饰器功能"""

    def test_alpha_decorator_valid_mixed_case(self):
        """测试有效的混合大小写字母"""
        alpha_test = AlphaTestModel(username='HelloWorld')
        result = sync_test_alpha_decorator(alpha_test=alpha_test)
        assert result == {'username': 'HelloWorld', 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    def test_alpha_decorator_valid_uppercase(self):
        """测试有效的纯大写字母"""
        alpha_test = AlphaTestModel(username='HELLO')
        result = sync_test_alpha_decorator(alpha_test=alpha_test)
        assert result == {'username': 'HELLO', 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    def test_alpha_decorator_valid_lowercase(self):
        """测试有效的纯小写字母"""
        alpha_test = AlphaTestModel(username='hello')
        result = sync_test_alpha_decorator(alpha_test=alpha_test)
        assert result == {'username': 'hello', 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    def test_alpha_decorator_empty_username(self):
        """测试空用户名"""
        alpha_test = AlphaTestModel()
        result = sync_test_alpha_decorator(alpha_test=alpha_test)
        assert result == {'username': None, 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    def test_alpha_decorator_invalid_with_numbers(self):
        """测试包含数字的无效用户名"""
        alpha_test = AlphaTestModel(username='hello123')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_alpha_decorator(alpha_test=alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert '用户名必须只包含字母' in error.message

    def test_alpha_decorator_invalid_with_special_chars(self):
        """测试包含特殊字符的无效用户名"""
        alpha_test = AlphaTestModel(username='hello@world')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_alpha_decorator(alpha_test=alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert '用户名必须只包含字母' in error.message

    def test_alpha_decorator_invalid_with_spaces(self):
        """测试包含空格的无效用户名"""
        alpha_test = AlphaTestModel(username='hello world')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_alpha_decorator(alpha_test=alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert '用户名必须只包含字母' in error.message

    def test_alpha_decorator_invalid_empty_string(self):
        """测试空字符串"""
        alpha_test = AlphaTestModel(username='')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_alpha_decorator(alpha_test=alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert '用户名必须只包含字母' in error.message

    def test_alpha_decorator_upper_mode_valid(self):
        """测试大写模式 - 有效输入"""
        alpha_test = AlphaTestModel(upper_name='HELLO')
        # 单独测试上大写字段
        try:
            alpha_test.get_upper_name()
        except FieldValidationError:
            pytest.fail('不应该抛出异常')

    def test_alpha_decorator_upper_mode_invalid_lowercase(self):
        """测试大写模式 - 包含小写字母的无效输入"""
        alpha_test = AlphaTestModel(upper_name='Hello')
        with pytest.raises(FieldValidationError) as exc_info:
            alpha_test.get_upper_name()

        error = exc_info.value
        assert error.field_name == 'upper_name'
        assert '名称必须只包含大写字母' in error.message

    def test_alpha_decorator_lower_mode_valid(self):
        """测试小写模式 - 有效输入"""
        alpha_test = AlphaTestModel(lower_name='hello')
        # 单独测试小写字段
        try:
            alpha_test.get_lower_name()
        except FieldValidationError:
            pytest.fail('不应该抛出异常')

    def test_alpha_decorator_lower_mode_invalid_uppercase(self):
        """测试小写模式 - 包含大写字母的无效输入"""
        alpha_test = AlphaTestModel(lower_name='Hello')
        with pytest.raises(FieldValidationError) as exc_info:
            alpha_test.get_lower_name()

        error = exc_info.value
        assert error.field_name == 'lower_name'
        assert '名称必须只包含小写字母' in error.message

    def test_alpha_decorator_default_message(self):
        """测试默认错误消息"""
        alpha_test = AlphaTestModel(mixed_name='hello123')
        with pytest.raises(FieldValidationError) as exc_info:
            alpha_test.get_mixed_name()

        error = exc_info.value
        assert error.field_name == 'mixed_name'
        assert 'mixed_name must contain only letters.' in error.message

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_valid_mixed_case(self):
        """测试异步装饰器有效的混合大小写字母"""
        alpha_test = AlphaTestModel(username='HelloWorld')
        result = await async_test_alpha_decorator(1, alpha_test)
        assert result == {'username': 'HelloWorld', 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_valid_uppercase(self):
        """测试异步装饰器有效的纯大写字母"""
        alpha_test = AlphaTestModel(username='HELLO')
        result = await async_test_alpha_decorator(1, alpha_test)
        assert result == {'username': 'HELLO', 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_valid_lowercase(self):
        """测试异步装饰器有效的纯小写字母"""
        alpha_test = AlphaTestModel(username='hello')
        result = await async_test_alpha_decorator(1, alpha_test)
        assert result == {'username': 'hello', 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_empty_username(self):
        """测试异步装饰器空用户名"""
        alpha_test = AlphaTestModel()
        result = await async_test_alpha_decorator(1, alpha_test)
        assert result == {'username': None, 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_invalid_with_numbers(self):
        """测试异步装饰器包含数字的无效用户名"""
        alpha_test = AlphaTestModel(username='hello123')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_alpha_decorator(1, alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert '用户名必须只包含字母' in error.message

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_invalid_with_special_chars(self):
        """测试异步装饰器包含特殊字符的无效用户名"""
        alpha_test = AlphaTestModel(username='hello@world')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_alpha_decorator(1, alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert '用户名必须只包含字母' in error.message

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_invalid_with_spaces(self):
        """测试异步装饰器包含空格的无效用户名"""
        alpha_test = AlphaTestModel(username='hello world')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_alpha_decorator(1, alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert '用户名必须只包含字母' in error.message

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_invalid_empty_string(self):
        """测试异步装饰器空字符串"""
        alpha_test = AlphaTestModel(username='')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_alpha_decorator(1, alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert '用户名必须只包含字母' in error.message

    def test_alpha_decorator_non_string_type(self):
        """测试非字符串类型的输入"""
        alpha_test = AlphaTestModel()
        # 设置一个非字符串类型的值（虽然 Pydantic 会尝试转换，但我们可以直接设置）
        alpha_test.__dict__['username'] = 123

        with pytest.raises(FieldValidationError) as exc_info:
            alpha_test.get_username()

        error = exc_info.value
        assert error.field_name == 'username'
        assert '用户名必须只包含字母' in error.message
