import pytest

import app as app_module
from app import app
from rate_limit import FixedWindowRateLimiter


@pytest.fixture
def client():
    app_module.limiter.reset()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def sample_features():
    return [0.0] * 22


def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'healthy'


def test_rejects_wrong_feature_count(client):
    response = client.post('/predict', json={'features': [0.0]})
    assert response.status_code == 400
    assert 'exactly 22' in response.get_json()['error']


def test_predict_returns_probability_and_label(client):
    response = client.post('/predict', json={'features': sample_features()})
    body = response.get_json()
    assert response.status_code == 200
    assert body['prediction'] in (0, 1)
    assert body['label'] in ('fraud', 'legitimate')
    assert 0 <= body['fraud_probability'] <= 1
    assert set(body['probability']) == {'0', '1'}
    assert response.headers['X-RateLimit-Remaining']


def test_predict_returns_429_after_client_limit(monkeypatch, client):
    monkeypatch.setattr(app_module, 'limiter', FixedWindowRateLimiter(limit=2, window_seconds=60))
    for _ in range(2):
        assert client.post('/predict', json={'features': sample_features()}).status_code == 200
    response = client.post('/predict', json={'features': sample_features()})
    assert response.status_code == 429
    assert response.get_json()['error'] == 'prediction rate limit exceeded'
    assert int(response.headers['Retry-After']) >= 1
