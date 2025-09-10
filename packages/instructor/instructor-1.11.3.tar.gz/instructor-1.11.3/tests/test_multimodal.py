import pytest
from pathlib import Path
from instructor.processing.multimodal import (
    PDF,
    Audio,
    Image,
    autodetect_media,
    convert_contents,
    convert_messages,
)
from instructor.mode import Mode
from unittest.mock import patch, MagicMock
import instructor


@pytest.fixture
def base64_jpeg():
    # Source: https://gist.github.com/trymbill/136dfd4bfc0736fae5b959430ec57373
    return "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAD8AKp//2Q=="  # noqa: E501


@pytest.fixture
def base64_png():
    # Source: https://gist.github.com/ondrek/7413434
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="  # noqa: E501


def test_image_from_url():
    url = "https://example.com/image.jpg"
    image = Image.from_url(url)
    assert image.source == url
    assert image.media_type == "image/jpeg"
    assert image.data is None


def test_image_from_path(tmp_path: Path):
    image_path = tmp_path / "test_image.jpg"
    image_path.write_bytes(b"fake image data")

    image = Image.from_path(image_path)
    assert image.source == image_path
    assert image.media_type == "image/jpeg"
    assert image.data is not None


@pytest.mark.skip(reason="Needs to download image")
def test_image_to_anthropic():
    image = Image(
        source="http://example.com/image.jpg", media_type="image/jpeg", data=None
    )
    anthropic_format = image.to_anthropic()
    assert anthropic_format["type"] == "image"
    assert anthropic_format["source"]["type"] == "base64"
    assert anthropic_format["source"]["media_type"] == "image/jpeg"


def test_image_to_openai():
    image = Image(
        source="http://example.com/image.jpg", media_type="image/jpeg", data=None
    )
    openai_format = image.to_openai(mode=instructor.Mode.TOOLS)
    assert openai_format["type"] == "image_url"
    assert openai_format["image_url"]["url"] == "http://example.com/image.jpg"


def test_convert_contents():
    contents = ["Hello", Image.from_url("http://example.com/image.jpg")]
    converted = list(convert_contents(contents, Mode.TOOLS))
    assert len(converted) == 2
    assert converted[0] == {"type": "text", "text": "Hello"}
    assert converted[1]["type"] == "image_url"
    assert converted[1]["image_url"]["url"] == "http://example.com/image.jpg"


def test_convert_messages():
    messages = [
        {
            "role": "user",
            "content": ["Hello", Image.from_url("http://example.com/image.jpg")],
        },
        {"role": "assistant", "content": "Hi there!"},
    ]
    converted = list(convert_messages(messages, Mode.TOOLS))
    assert len(converted) == 2
    assert converted[0]["role"] == "user"
    assert len(converted[0]["content"]) == 2
    assert converted[0]["content"][0] == {"type": "text", "text": "Hello"}
    assert converted[0]["content"][1]["type"] == "image_url"
    assert converted[1]["role"] == "assistant"
    assert converted[1]["content"] == "Hi there!"


def test_convert_messages_anthropic():
    messages = [
        {
            "role": "user",
            "content": [
                "Hello",
                Image(source="base64data", media_type="image/jpeg", data="fakedata"),
            ],
        }
    ]
    converted = list(convert_messages(messages, Mode.ANTHROPIC_JSON))
    assert len(converted) == 1
    assert converted == [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Hello"},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": "fakedata",
                    },
                },
            ],
        }
    ]


def test_convert_messages_gemini():
    messages = [
        {
            "role": "user",
            "content": ["Hello", Image.from_url("http://example.com/image.jpg")],
        }
    ]
    with pytest.raises(NotImplementedError):
        list(convert_messages(messages, Mode.GEMINI_JSON))


# Additional tests


def test_image_from_path_unsupported_format(tmp_path: Path):
    image_path = tmp_path / "test_image.txt"
    image_path.write_bytes(b"fake gif data")

    with pytest.raises(ValueError, match="Unsupported image format: text/plain"):
        Image.from_path(image_path)


def test_image_from_path_empty_file(tmp_path: Path):
    image_path = tmp_path / "empty_image.jpg"
    image_path.touch()

    with pytest.raises(ValueError, match="Image file is empty"):
        Image.from_path(image_path)


def test_image_to_openai_base64():
    image = Image(
        source="local_file.jpg", media_type="image/jpeg", data="base64encodeddata"
    )
    openai_format = image.to_openai(mode=instructor.Mode.TOOLS)
    assert openai_format["type"] == "image_url"
    assert openai_format["image_url"]["url"].startswith("data:image/jpeg;base64,")


def test_convert_contents_single_string():
    content = "Hello, world!"
    converted = convert_contents(content, Mode.TOOLS)
    assert converted == "Hello, world!"


def test_convert_contents_single_image():
    image = Image.from_url("http://example.com/image.jpg")
    converted = list(convert_contents(image, Mode.TOOLS))
    assert len(converted) == 1
    assert converted == [
        {"type": "image_url", "image_url": {"url": "http://example.com/image.jpg"}}
    ]


def test_convert_messages_mixed_content():
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": Image.from_url("http://example.com/image.jpg")},
    ]
    converted = list(convert_messages(messages, Mode.TOOLS))
    assert len(converted) == 3
    assert converted[0]["content"] == "Hello"
    assert converted[1]["content"] == "Hi there!"
    assert converted[2]["content"][0]["type"] == "image_url"


def test_convert_contents_invalid_type():
    with pytest.raises(ValueError, match="Unsupported content type"):
        list(convert_contents([1, 2, 3], Mode.TOOLS))


def test_convert_contents_anthropic_mode():
    contents = [
        "Hello",
        Image(source="base64data", media_type="image/png", data="fakedata"),
    ]
    converted = list(convert_contents(contents, Mode.ANTHROPIC_JSON))
    assert converted[1]["type"] == "image"
    assert converted[1]["source"]["type"] == "base64"
    assert converted[1]["source"]["media_type"] == "image/png"


def test_convert_contents_custom_dict():
    contents = {
        "type": "image_url",
        "image_url": {"url": f"data:image/png;base64,base64_img"},
    }
    converted = list(convert_contents(contents, Mode.TOOLS))
    assert len(converted) == 1
    assert converted == [contents]


def test_image_from_base64_url(base64_png):
    image = Image.from_url(base64_png)
    assert image.source == base64_png
    assert image.media_type == "image/png"
    assert image.data is not None
    assert image.data == base64_png.split(",")[-1]


def test_image_from_url_with_query_params():
    url = "https://example.com/image.jpg?param1=value1&param2=value2"
    image = Image.from_url(url)
    assert image.source == url
    assert image.media_type == "image/jpeg"
    assert image.data is None


def test_image_from_url_with_unusual_extension():
    url = "https://example.com/image.webp"
    image = Image.from_url(url)
    assert image.source == url
    assert image.media_type == "image/webp"
    assert image.data is None


def test_image_to_openai_with_base64_source(base64_png):
    base64_data = base64_png.split(",")[-1]
    image = Image(
        source=f"data:image/png;base64,{base64_data}",
        media_type="image/png",
        data=base64_data,
    )
    openai_format = image.to_openai(mode=instructor.Mode.TOOLS)
    assert openai_format["type"] == "image_url"
    assert openai_format["image_url"]["url"] == f"data:image/png;base64,{base64_data}"


def test_image_to_anthropic_with_base64_source(base64_png):
    base64_data = base64_png.split(",")[-1]
    image = Image(
        source=f"data:image/png;base64,{base64_data}",
        media_type="image/png",
        data=base64_data,
    )
    anthropic_format = image.to_anthropic()
    assert anthropic_format["type"] == "image"
    assert anthropic_format["source"]["type"] == "base64"
    assert anthropic_format["source"]["media_type"] == "image/png"
    assert anthropic_format["source"]["data"] == base64_data


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/image.jpg",
        "https://example.com/image.png",
        "https://example.com/image.webp",
        "https://example.com/image.jpg?param=value",
        "base64_png",
    ],
)
def test_image_from_various_urls(url, request):
    if url.startswith("base64"):
        url = request.getfixturevalue(url)
    image = Image.from_url(url)
    assert image.source == url
    if image.is_base64(url):
        assert image.data is not None
    else:
        assert image.data is None


def test_convert_contents_with_base64_image(base64_png):
    contents = ["Hello", Image.from_url(base64_png)]
    converted = list(convert_contents(contents, Mode.TOOLS))
    assert len(converted) == 2
    assert converted[0] == {"type": "text", "text": "Hello"}
    assert converted[1]["type"] == "image_url"
    assert converted[1]["image_url"]["url"] == base64_png


@pytest.mark.parametrize(
    "input_data, expected_type, expected_media_type",
    [
        # URL tests
        ("http://example.com/image.jpg", "url", "image/jpeg"),
        ("https://example.com/image.png", "url", "image/png"),
        ("https://example.com/image.webp", "url", "image/webp"),
        ("https://example.com/image.jpg?param=value", "url", "image/jpeg"),
        (
            "https://example.com/image",
            "url",
            "image/jpeg",
        ),  # Default to JPEG if no extension
        # Base64 data URI tests
        (
            "base64_png",
            "base64",
            "image/png",
        ),
        (
            "base64_jpeg",
            "base64",
            "image/jpeg",
        ),
        # File path tests (mocked)
        ("/path/to/image.jpg", "file", "image/jpeg"),
        ("/path/to/image.png", "file", "image/png"),
        ("/path/to/image.webp", "file", "image/webp"),
    ],
)
def test_image_autodetect(input_data, expected_type, expected_media_type, request):
    with (
        patch("pathlib.Path.is_file", return_value=True),
        patch("pathlib.Path.stat", return_value=MagicMock(st_size=1000)),
        patch("pathlib.Path.read_bytes", return_value=b"fake image data"),
        patch("requests.head") as mock_head,
    ):
        mock_head.return_value = MagicMock(
            headers={"Content-Type": expected_media_type}
        )
        if input_data.startswith("base64"):
            input_data = request.getfixturevalue(input_data)

        image = Image.autodetect(input_data)

        if isinstance(image.source, Path):
            assert image.source == Path(input_data)
        else:
            assert image.source == input_data
        assert image.media_type == expected_media_type

        if expected_type == "url":
            assert image.data is None
        elif expected_type == "base64":
            assert image.data is not None
            assert image.data.startswith("iVBOR") or image.data.startswith("/9j/")
        elif expected_type == "file":
            assert image.data is not None
            assert image.data == "ZmFrZSBpbWFnZSBkYXRh"  # base64 of 'fake image data'


def test_image_autodetect_invalid_input():
    with pytest.raises(ValueError, match="Invalid or unsupported base64 image data"):
        Image.autodetect("not_an_image_input")

    # Test safely converting an invalid image
    assert Image.autodetect_safely("hello") == "hello"


def test_image_autodetect_empty_file(tmp_path):
    empty_file = tmp_path / "empty.jpg"
    empty_file.touch()
    with pytest.raises(ValueError, match="Image file is empty"):
        Image.autodetect(empty_file)


def test_raw_base64_autodetect_jpeg(base64_jpeg):
    raw_base_64 = base64_jpeg.split(",")[-1]
    image = Image.autodetect(raw_base_64)
    assert image.media_type == "image/jpeg"
    assert image.source == image.data == raw_base_64


def test_raw_base64_autodetect_png(base64_png):
    raw_base_64 = base64_png.split(",")[-1]
    image = Image.autodetect(raw_base_64)
    assert image.media_type == "image/png"
    assert image.source == image.data == raw_base_64


def test_autodetect_media_data_uris():
    img_uri = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
    )
    pdf_uri = "data:application/pdf;base64,JVBERi0xLjQK"  # "%PDF-1.4\n"
    aud_uri = "data:audio/wav;base64,UklGRiQAAABXQVZF"  # minimal header-ish

    img = autodetect_media(img_uri)
    pdf = autodetect_media(pdf_uri)
    aud = autodetect_media(aud_uri)

    assert isinstance(img, Image)
    assert img.media_type == "image/png"

    assert isinstance(pdf, PDF)
    assert pdf.media_type == "application/pdf"

    assert isinstance(aud, Audio)
    assert aud.media_type == "audio/wav"


def test_convert_messages_autodetect_media():
    img_uri = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
    )
    pdf_uri = "data:application/pdf;base64,JVBERi0xLjQK"

    messages = [
        {"role": "user", "content": ["hello", img_uri, pdf_uri]},
    ]

    out = convert_messages(messages, mode=Mode.RESPONSES_TOOLS, autodetect_images=True)
    assert isinstance(out, list) and len(out) == 1

    content = out[0]["content"]
    assert isinstance(content, list) and len(content) == 3

    # Text
    assert content[0]["type"] in {"input_text", "text"}
    assert content[0]["text"] == "hello"

    # Image → input_image with data URI
    assert content[1]["type"] == "input_image"
    assert isinstance(content[1].get("image_url"), str)
    assert content[1]["image_url"].startswith("data:image/png;base64,")

    # PDF → input_file with data URI
    assert content[2]["type"] == "input_file"
    assert isinstance(content[2].get("file_data"), str)
    assert content[2]["file_data"].startswith("data:application/pdf;base64,")


def test_pdf_from_url():
    # URL without extension → should HEAD and set media_type; data stays None.
    with patch("instructor.processing.multimodal.requests.head") as mock_head:
        resp = MagicMock()
        resp.headers = {"Content-Type": "application/pdf"}
        resp.raise_for_status = MagicMock()
        mock_head.return_value = resp

        pdf = PDF.from_url("https://example.com/file")

    assert isinstance(pdf, PDF)
    assert pdf.source == "https://example.com/file"
    assert pdf.media_type == "application/pdf"
    assert pdf.data is None


def test_pdf_from_gs_url():
    # gs:// → https://storage.googleapis.com/... (GET) and bytes are base64-encoded.
    pdf_bytes = b"%PDF-1.4\n..."
    with patch("instructor.processing.multimodal.requests.get") as mock_get:
        resp = MagicMock()
        resp.headers = {"Content-Type": "application/pdf"}
        resp.content = pdf_bytes
        resp.raise_for_status = MagicMock()
        mock_get.return_value = resp

        pdf = PDF.from_gs_url("gs://bucket/doc.pdf")

    assert isinstance(pdf, PDF)
    assert pdf.source == "gs://bucket/doc.pdf"
    assert pdf.media_type == "application/pdf"
    # Optional strictness without adding global imports:
    import base64 as _b64

    assert pdf.data == _b64.b64encode(pdf_bytes).decode("utf-8")


def test_audio_from_url():
    # Audio URL → GET; implementation reads headers.get('content-type')
    audio_bytes = b"RIFFxxxxWAVEfmt "
    with patch("instructor.processing.multimodal.requests.get") as mock_get:
        resp = MagicMock()
        resp.headers = {"content-type": "audio/wav"}
        resp.content = audio_bytes
        resp.raise_for_status = MagicMock()
        mock_get.return_value = resp

        audio = Audio.from_url("https://cdn.example.com/a.wav")

    assert isinstance(audio, Audio)
    assert audio.source == "https://cdn.example.com/a.wav"
    assert audio.media_type == "audio/wav"
    import base64 as _b64

    assert audio.data == _b64.b64encode(audio_bytes).decode("utf-8")


def test_audio_from_gs_url():
    # gs:// audio → public GCS GET and base64-encode.
    audio_bytes = b"\x00\x01\x02\x03"
    with patch("instructor.processing.multimodal.requests.get") as mock_get:
        resp = MagicMock()
        resp.headers = {"Content-Type": "audio/mpeg"}
        resp.content = audio_bytes
        resp.raise_for_status = MagicMock()
        mock_get.return_value = resp

        audio = Audio.from_gs_url("gs://bkt/path/song.mp3")

    assert isinstance(audio, Audio)
    assert audio.source == "gs://bkt/path/song.mp3"
    assert audio.media_type == "audio/mpeg"
    import base64 as _b64

    assert audio.data == _b64.b64encode(audio_bytes).decode("utf-8")


def test_audio_from_base64():
    # data:audio/* data URI → parsed without network.
    import base64 as _b64

    raw = b"\x11\x22\x33\x44"
    uri = "data:audio/wav;base64," + _b64.b64encode(raw).decode("utf-8")

    audio = Audio.from_base64(uri)

    assert isinstance(audio, Audio)
    assert audio.source == uri
    assert audio.media_type == "audio/wav"
    assert audio.data == _b64.b64encode(raw).decode("utf-8")
