"""
Comprehensive Encoding and Unicode Test Suite for AI-Optimized Logging System.

Tests unicode handling, encoding validation, and international character support
to ensure robust logging across different character sets and languages.
"""

import json
import pytest
import tempfile
import os
from pathlib import Path
from src.logging_system.logger_config import configure_ai_logging, get_ai_logger, reset_logging_state


class TestUnicodeSupport:
    """Test unicode character handling in log messages and context."""
    
    def setup_method(self):
        """Reset logging state before each test."""
        reset_logging_state()
        configure_ai_logging(log_level="DEBUG", console_output=False)
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_logging_state()
    
    def test_unicode_log_messages(self):
        """Test logging messages with unicode characters."""
        logger = get_ai_logger("test_unicode")
        
        # Test various unicode characters
        unicode_messages = [
            "English text",
            "Русский текст",
            "中文文本",
            "العربية",
            "Français avec accénts",
            "Emoji support 🚀💰📈",
            "Math symbols: ∑∂∆√∞",
            "Currency: €£¥₹₿"
        ]
        
        for message in unicode_messages:
            # Should not raise encoding errors
            logger.info(message, operation="unicode_test", 
                       context={"message_type": "unicode", "length": len(message)})
    
    def test_unicode_context_data(self):
        """Test unicode characters in context dictionaries."""
        logger = get_ai_logger("test_unicode_context")
        
        unicode_context = {
            "user_name": "Георгий",
            "city": "北京",
            "description": "Тест с разными языками and emoji 🌍",
            "currency_symbol": "€",
            "math_formula": "∑(x²) = ∞",
            "mixed": "English + Русский + 中文"
        }
        
        # Should handle unicode in context without errors
        logger.info("Testing unicode context", 
                   operation="unicode_context_test",
                   context=unicode_context)
    
    def test_unicode_operation_names(self):
        """Test unicode characters in operation names."""
        logger = get_ai_logger("test_unicode_operations")
        
        # Test various unicode operation names
        operations = [
            "数据处理",
            "обработка_данных", 
            "معالجة_البيانات",
            "データ処理",
            "traitement_données"
        ]
        
        for operation in operations:
            logger.debug("Unicode operation test",
                        operation=operation,
                        context={"operation_type": "unicode"})


class TestEncodingValidation:
    """Test encoding validation and error handling."""
    
    def setup_method(self):
        """Reset logging state before each test."""
        reset_logging_state()
        configure_ai_logging(log_level="DEBUG", console_output=False)
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_logging_state()
    
    def test_json_serialization_unicode(self):
        """Test JSON serialization with unicode data."""
        logger = get_ai_logger("test_json_unicode")
        
        complex_unicode_data = {
            "strings": ["Hello", "Привет", "こんにちは", "مرحبا"],
            "nested": {
                "description": "Multi-language support test 🌐",
                "numbers": [1, 2, 3],
                "boolean": True,
                "null_value": None
            },
            "emoji_data": "🚀💰📈📊💹",
            "special_chars": "!@#$%^&*()_+-={}[]|\\:;\"'<>?,./"
        }
        
        # Should serialize to valid JSON without encoding errors
        logger.info("Complex unicode data test",
                   operation="json_unicode_test",
                   context=complex_unicode_data)
    
    def test_binary_data_handling(self):
        """Test handling of binary data in context."""
        logger = get_ai_logger("test_binary")
        
        # Binary data should be converted to string representation
        binary_data = b'\x00\x01\x02\x03\xff\xfe\xfd'
        
        context = {
            "binary_raw": str(binary_data),
            "binary_hex": binary_data.hex(),
            "mixed_data": "text with binary: " + str(binary_data)
        }
        
        logger.warning("Binary data in context",
                      operation="binary_handling_test",
                      context=context)
    
    def test_large_unicode_strings(self):
        """Test handling of large unicode strings."""
        logger = get_ai_logger("test_large_unicode")
        
        # Create large unicode string with mixed characters
        large_unicode = "🌍" * 1000 + "Русский" * 500 + "中文" * 300
        
        context = {
            "large_string": large_unicode,
            "string_length": len(large_unicode),
            "byte_length": len(large_unicode.encode('utf-8'))
        }
        
        logger.info("Large unicode string test",
                   operation="large_unicode_test",
                   context=context)


class TestFileEncodingOutput:
    """Test file output with various encodings."""
    
    def test_utf8_file_output(self):
        """Test UTF-8 file output with unicode content."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
            temp_path = temp_file.name
        
        try:
            reset_logging_state()
            configure_ai_logging(log_level="DEBUG", 
                                log_file=temp_path,
                                console_output=False)
            
            logger = get_ai_logger("test_file_utf8")
            
            # Log unicode content
            unicode_messages = [
                "ASCII text",
                "Русский текст с ёлками 🌲",
                "中文消息 with mixed content",
                "Émojis and spéciål chärs: 🚀💰📈"
            ]
            
            for msg in unicode_messages:
                logger.info(msg, 
                           operation="file_utf8_test",
                           context={"message": msg, "encoding": "utf-8"})
            
            reset_logging_state()
            
            # Verify file contains valid UTF-8
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0
                
                # Verify unicode characters are preserved
                assert "Русский" in content
                assert "中文" in content
                assert "🚀" in content
                
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_json_structure_with_unicode(self):
        """Test that JSON structure is maintained with unicode content."""
        reset_logging_state()
        configure_ai_logging(log_level="INFO",
                            log_file=None,
                            console_output=True)
        
        logger = get_ai_logger("test_json_structure")
        
        unicode_context = {
            "user": "Дмитрий",
            "action": "购买",
            "amount": "€1,234.56",
            "status": "成功 ✅"
        }
        
        # Just test that logging with unicode doesn't crash
        try:
            logger.info("Unicode transaction completed",
                       operation="transaction_unicode",
                       context=unicode_context)
            
            # If we get here, unicode logging works
            unicode_test_passed = True
        except Exception as e:
            unicode_test_passed = False
            
        reset_logging_state()
        
        assert unicode_test_passed, "Unicode logging failed with exception"
        
        # Test JSON serialization directly
        import json
        try:
            json_str = json.dumps(unicode_context, ensure_ascii=False)
            parsed_back = json.loads(json_str)
            
            assert parsed_back["user"] == "Дмитрий"
            assert parsed_back["action"] == "购买"
            assert parsed_back["amount"] == "€1,234.56"
            assert parsed_back["status"] == "成功 ✅"
            
        except Exception as e:
            assert False, f"JSON serialization of unicode failed: {e}"


class TestSpecialCharacterHandling:
    """Test handling of special characters and edge cases."""
    
    def setup_method(self):
        """Reset logging state before each test."""
        reset_logging_state()
        configure_ai_logging(log_level="DEBUG", console_output=False)
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_logging_state()
    
    def test_json_escape_characters(self):
        """Test proper escaping of JSON special characters."""
        logger = get_ai_logger("test_json_escape")
        
        # Characters that need escaping in JSON
        special_chars = {
            "quote": 'String with "quotes"',
            "backslash": "Path\\to\\file",
            "newline": "Line 1\nLine 2",
            "tab": "Column1\tColumn2",
            "carriage_return": "Text\rwith CR",
            "mixed": "Complex \"string\" with\n\ttabs and \\backslashes"
        }
        
        logger.info("Testing JSON escape characters",
                   operation="json_escape_test",
                   context=special_chars)
    
    def test_control_characters(self):
        """Test handling of control characters."""
        logger = get_ai_logger("test_control_chars")
        
        # Various control characters
        control_chars = {
            "null_char": "Text\x00with null",
            "bell": "Alert\x07sound",
            "form_feed": "Page\x0cbreak",
            "vertical_tab": "Vertical\x0btab",
            "escape": "ESC\x1bsequence"
        }
        
        # Should handle control characters without crashing
        logger.warning("Control characters in data",
                      operation="control_char_test",
                      context=control_chars)
    
    def test_normalization_forms(self):
        """Test different Unicode normalization forms."""
        logger = get_ai_logger("test_normalization")
        
        # Same character in different Unicode forms
        import unicodedata
        
        # Café in different normalization forms
        cafe_nfc = "café"  # NFC form
        cafe_nfd = unicodedata.normalize('NFD', "café")  # NFD form
        
        context = {
            "text_nfc": cafe_nfc,
            "text_nfd": cafe_nfd,
            "are_equal": cafe_nfc == cafe_nfd,
            "nfc_length": len(cafe_nfc),
            "nfd_length": len(cafe_nfd)
        }
        
        logger.debug("Unicode normalization test",
                    operation="normalization_test",
                    context=context)


class TestEncodingErrorRecovery:
    """Test error recovery from encoding issues."""
    
    def setup_method(self):
        """Reset logging state before each test."""
        reset_logging_state()
        configure_ai_logging(log_level="DEBUG", console_output=False)
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_logging_state()
    
    def test_non_serializable_objects(self):
        """Test handling of non-JSON-serializable objects with unicode."""
        logger = get_ai_logger("test_non_serializable")
        
        class UnicodeTestClass:
            def __init__(self):
                self.name = "Тестовый класс"
                self.description = "测试类"
            
            def __str__(self):
                return f"UnicodeTestClass(name={self.name})"
        
        test_obj = UnicodeTestClass()
        
        # Should convert to string representation without errors
        context = {
            "object": test_obj,
            "object_str": str(test_obj),
            "unicode_attr": test_obj.name
        }
        
        logger.info("Non-serializable object with unicode",
                   operation="serialization_test",
                   context=context)
    
    def test_circular_reference_with_unicode(self):
        """Test handling of circular references containing unicode."""
        logger = get_ai_logger("test_circular_unicode")
        
        # Create circular reference with unicode data
        obj_a = {"name": "对象A", "ref": None}
        obj_b = {"name": "Объект Б", "ref": obj_a}
        obj_a["ref"] = obj_b
        
        # Should handle circular reference gracefully
        context = {
            "circular_obj": str(obj_a),
            "description": "Circular reference with unicode names"
        }
        
        logger.warning("Circular reference with unicode data",
                      operation="circular_ref_test",
                      context=context)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])