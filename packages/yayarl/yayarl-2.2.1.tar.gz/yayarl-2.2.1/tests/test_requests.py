import requests

from yayarl import URL

base_url = URL("https://jsonplaceholder.typicode.com")


def test_get():
    url = base_url / "todos" / 1

    resp = url.get(timeout=10)
    data = resp.json()

    assert resp.status_code == 200
    assert data["userId"] == 1


def test_post():
    url = base_url / "posts"

    resp = url.post(json={"title": "Example"}, timeout=10)

    assert resp.status_code == 201
    assert resp.json()["title"] == "Example"


def test_delete():
    url = base_url / "posts" / 1

    resp = url.delete()

    assert resp.status_code == 200


def test_session():
    with requests.Session() as session:
        url = base_url / "posts" / 1 / "comments"
        resp = url.get(session=session)
        assert resp.status_code == 200
        assert resp.json()

        # link session:
        url_with_session = url & session
        # original url should not have changed!
        assert url_with_session._default_session
        assert getattr(url, "_default_session", None) is None
        url &= session
        assert url_with_session._default_session is url._default_session

        resp = url_with_session.get()
        assert resp.status_code == 200
        assert resp.json()
