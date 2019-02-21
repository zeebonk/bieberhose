from bieberhose import credentials


def test__load_and_save(tmp_path):
    credentials.CREDENTIALS_PATH = tmp_path / ".creds"

    credentials.save({"foo": "bar"})
    assert credentials.load() == {"foo": "bar"}


def test__exists(tmp_path):
    credentials.CREDENTIALS_PATH = tmp_path / ".creds"

    assert not credentials.exists()
    credentials.save({"foo": "bar"})
    assert credentials.exists()
