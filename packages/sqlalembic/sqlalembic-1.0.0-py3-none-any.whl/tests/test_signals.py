import pytest
from unittest.mock import MagicMock, patch
from sqlalembic.core.signals import dispatcher, SignalDispatcher

@pytest.fixture(autouse=True)
def clean_dispatcher():
    """تنظيف الـ registry قبل وبعد كل اختبار."""
    dispatcher._registry.clear()
    yield
    dispatcher._registry.clear()

@pytest.fixture
def fresh_dispatcher():
    """إنشاء dispatcher جديد للاختبارات المعزولة."""
    return SignalDispatcher()

def test_signal_connection_and_dispatch():
    """اختبار ربط واستدعاء المعالج عند إرسال الإشارة."""
    results = []
    
    def my_handler(sender, **kwargs):
        results.append(kwargs.get("message"))
        
    dispatcher.connect("test_signal", my_handler)
    dispatcher.send("test_signal", sender=None, message="hello_world")
    
    assert "hello_world" in results

def test_multiple_handlers_for_one_signal():
    """اختبار أن إشارة واحدة تستدعي عدة معالجات."""
    results = []
    
    def handler1(sender, **kwargs):
        results.append("handler1 called")

    def handler2(sender, **kwargs):
        results.append("handler2 called")
        
    dispatcher.connect("test_signal", handler1)
    dispatcher.connect("test_signal", handler2)
    dispatcher.send("test_signal", sender=None)
    
    assert "handler1 called" in results
    assert "handler2 called" in results
    assert len(results) == 2

def test_signal_disconnection():
    """اختبار أن المعالج لا يُستدعى بعد فصله."""
    results = []
    
    def my_handler(sender, **kwargs):
        results.append("handler called")
        
    dispatcher.connect("test_signal", my_handler)
    dispatcher.disconnect("test_signal", my_handler)
    
    dispatcher.send("test_signal", sender=None)
    
    assert not results

def test_signal_with_data():
    """اختبار أن البيانات يتم تمريرها بشكل صحيح."""
    received_data = {}
    received_sender = None
    
    def my_handler(sender, **kwargs):
        nonlocal received_sender
        received_sender = sender
        received_data.update(kwargs)
        
    dispatcher.connect("data_signal", my_handler)
    dispatcher.send("data_signal", sender="test_sender", value=42, status="success")
    
    assert received_data.get("value") == 42
    assert received_data.get("status") == "success"
    assert received_sender == "test_sender"

def test_connect_invalid_signal_name(fresh_dispatcher):
    """اختبار التعامل مع أسماء signals غير صحيحة."""
    def dummy_handler(sender, **kwargs):
        pass
    
    fresh_dispatcher.connect("", dummy_handler)
    assert "" not in fresh_dispatcher._registry
    
    fresh_dispatcher.connect(123, dummy_handler)
    assert 123 not in fresh_dispatcher._registry

def test_connect_invalid_receiver(fresh_dispatcher):
    """اختبار التعامل مع receivers غير صحيحة."""
    fresh_dispatcher.connect("test_signal", "not_callable")
    assert "test_signal" not in fresh_dispatcher._registry
    
    fresh_dispatcher.connect("test_signal", 123)
    assert "test_signal" not in fresh_dispatcher._registry

def test_connect_duplicate_receiver():
    """اختبار عدم إضافة نفس الـ receiver مرتين."""
    def my_handler(sender, **kwargs):
        pass
    
    dispatcher.connect("test_signal", my_handler)
    dispatcher.connect("test_signal", my_handler)
    
    assert len(dispatcher._registry["test_signal"]) == 1

def test_disconnect_invalid_signal_name(fresh_dispatcher):
    """اختبار التعامل مع أسماء signals غير صحيحة في disconnect."""
    def dummy_handler(sender, **kwargs):
        pass
    
    fresh_dispatcher.disconnect("", dummy_handler)
    fresh_dispatcher.disconnect(123, dummy_handler)

def test_disconnect_invalid_receiver(fresh_dispatcher):
    """اختبار التعامل مع receivers غير صحيحة في disconnect."""
    fresh_dispatcher.disconnect("test_signal", "not_callable")
    fresh_dispatcher.disconnect("test_signal", 123)

def test_disconnect_nonexistent_signal():
    """اختبار فصل receiver من signal غير موجود."""
    def my_handler(sender, **kwargs):
        pass
    
    dispatcher.disconnect("nonexistent_signal", my_handler)

def test_disconnect_nonexistent_receiver():
    """اختبار فصل receiver غير موجود من signal موجود."""
    def handler1(sender, **kwargs):
        pass
    
    def handler2(sender, **kwargs):
        pass
    
    dispatcher.connect("test_signal", handler1)
    dispatcher.disconnect("test_signal", handler2)
    
    assert len(dispatcher._registry["test_signal"]) == 1

def test_send_invalid_signal_name(fresh_dispatcher):
    """اختبار إرسال signal باسم غير صحيح."""
    result = fresh_dispatcher.send("")
    assert result == []
    
    result = fresh_dispatcher.send(123)
    assert result == []

def test_send_nonexistent_signal():
    """اختبار إرسال signal غير موجود."""
    result = dispatcher.send("nonexistent_signal")
    assert result == []

def test_send_returns_results():
    """اختبار أن send ترجع نتائج الـ receivers."""
    def handler1(sender, **kwargs):
        return "result1"
    
    def handler2(sender, **kwargs):
        return "result2"
    
    dispatcher.connect("test_signal", handler1)
    dispatcher.connect("test_signal", handler2)
    
    results = dispatcher.send("test_signal")
    
    assert len(results) == 2
    returned_values = [result[1] for result in results]
    assert "result1" in returned_values
    assert "result2" in returned_values

def test_send_with_receiver_exception():
    """اختبار التعامل مع الأخطاء في الـ receivers."""
    results = []
    
    def good_handler(sender, **kwargs):
        results.append("success")
        return "good"
    
    def bad_handler(sender, **kwargs):
        raise ValueError("Test error")
    
    dispatcher.connect("test_signal", good_handler)
    dispatcher.connect("test_signal", bad_handler)
    
    send_results = dispatcher.send("test_signal")

    assert "success" in results
    

    assert len(send_results) == 2
    exceptions = [result[1] for result in send_results if isinstance(result[1], Exception)]
    assert len(exceptions) == 1
    assert isinstance(exceptions[0], ValueError)

def test_registry_cleanup_after_disconnect():
    """اختبار أن الـ signal يتم حذفه من الـ registry بعد فصل آخر receiver."""
    def my_handler(sender, **kwargs):
        pass
    
    dispatcher.connect("test_signal", my_handler)
    assert "test_signal" in dispatcher._registry
    
    dispatcher.disconnect("test_signal", my_handler)
    assert "test_signal" not in dispatcher._registry

def test_fresh_dispatcher_initialization(fresh_dispatcher):
    """اختبار أن dispatcher جديد يبدأ بـ registry فارغ."""
    assert fresh_dispatcher._registry == {}

@patch('sqlalembic.core.signals.logger')
def test_logging_on_connect(mock_logger, fresh_dispatcher):
    """اختبار أن الـ logging يشتغل في connect."""
    def my_handler(sender, **kwargs):
        pass
    
    fresh_dispatcher.connect("test_signal", my_handler)
    
    mock_logger.info.assert_called()
    mock_logger.debug.assert_called()

@patch('sqlalembic.core.signals.logger')
def test_logging_on_send_error(mock_logger, fresh_dispatcher):
    """اختبار أن الـ logging يشتغل عند حدوث خطأ في receiver."""
    def error_handler(sender, **kwargs):
        raise Exception("Test error")
    
    fresh_dispatcher.connect("test_signal", error_handler)
    fresh_dispatcher.send("test_signal")
    
    mock_logger.error.assert_called()