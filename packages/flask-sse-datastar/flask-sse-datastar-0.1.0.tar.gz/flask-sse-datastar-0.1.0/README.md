### Flask SSE Datastar [![Build Status](https://github.com/singingwolfboy/flask-sse/workflows/Test/badge.svg)](https://github.com/singingwolfboy/flask-sse/actions?query=workflow%3ATest) [![Test Coverage](http://codecov.io/github/singingwolfboy/flask-sse/coverage.svg?branch=master)](http://codecov.io/github/singingwolfboy/flask-sse?branch=master) [![Documentation](https://readthedocs.org/projects/flask-sse/badge/?version=latest&style=flat)](http://flask-sse.readthedocs.org/)

A Flask extension for HTML5 [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) support, powered by [Redis](http://www.redis.io/).

This version has had a minor change so that it works with [Datastar](https://data-star.dev/).

### Example of sending events:

```python
from flask import Flask
from flask_sse import sse

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')

@app.route('/send')
def send_message():
    sse.publish({"message": "Hello!"}, type='greeting')
    return "Message sent!"
```
To receive events on a webpage, use Javascript to connect to the event stream, like this:
```JavaScript

var source = new EventSource("{{ url_for('sse.stream') }}");
source.addEventListener('greeting', function(event) {
    var data = JSON.parse(event.data);
    // do what you want with this data
}, false);
```
The full documentation for this project is hosted on ReadTheDocs.
