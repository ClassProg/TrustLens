from io import BytesIO
from PIL import Image
import pytest
from app import app

@pytest.fixture
def client():
    app.config.update(TESTING=True)
    return app.test_client()

def image_bytes(fmt='PNG'):
    out=BytesIO()
    Image.new('RGB',(24,24),(70,130,80)).save(out,format=fmt)
    out.seek(0)
    return out

def test_health(client):
    response=client.get('/api/health')
    assert response.status_code==200
    assert response.json['status']=='ok'
    assert response.json['mock_mode'] is True

def test_models(client):
    response=client.get('/api/models')
    assert {m['id'] for m in response.json}=={'resnet50','densenet121'}

def test_missing_image(client):
    response=client.post('/api/analyze',data={'model':'resnet50'})
    assert response.status_code==400
    assert 'error' in response.json

def test_invalid_model(client):
    response=client.post('/api/analyze',data={'model':'unknown','file':(image_bytes(),'retina.png')})
    assert response.status_code==400

def test_valid_png_returns_mock_schema(client):
    response=client.post('/api/analyze',data={'model':'resnet50','file':(image_bytes(),'retina.png')})
    assert response.status_code==200
    result=response.json
    assert result['demo_mode'] is True
    assert len(result['explanations'])==3
    assert result['quantus']['source']=='mock'
    assert result['expert_disagreement']['available'] is False

def test_valid_jpeg(client):
    response=client.post('/api/analyze',data={'file':(image_bytes('JPEG'),'retina.jpg')})
    assert response.status_code==200

def test_corrupt_image(client):
    response=client.post('/api/analyze',data={'file':(BytesIO(b'not an image'),'bad.png')})
    assert response.status_code==400
    assert 'error' in response.json

def test_unsupported_format(client):
    response=client.post('/api/analyze',data={'file':(image_bytes('GIF'),'retina.gif')})
    assert response.status_code==400
