# Intro to Observability: OpenTelemetry in Python

This application is here for you to try out tracing.
It consists of a microservice that calls itself, so you can simulate
a whole microservice ecosystem with just one service!

Spoiler: this microservice implements the <a href="https://en.wikipedia.org/wiki/Fibonacci_number">Fibonacci sequence</a>.

## What to do

Recommended:
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/honeycombio/intro-to-o11y-python)

Alternative: [remix this app on Glitch](https://glitch.com/edit/#!/intro-to-o11y-python).

Or, if you prefer to work on your own computer...

### Running locally

Clone this repository.

If you use [VSCode devcontainers](https://code.visualstudio.com/docs/remote/containers-tutorial),
then reopen in a container. Otherwise, have python 3 and pip installed.

```shell
pip3 install --user -r requirements.txt
PYTHONUNBUFFERED=true
python3 server.py
```

Hit the app at http://localhost:5000

once that works, stop the app and configure it to send traces.

#### Configure the Agent

Tell OpenTelemetry to send events to Honeycomb.
In `.env` in glitch or your run configuration in your IDE, add these
environment variables:

```sh
HONEYCOMB_API_KEY=replace-this-with-a-real-api-key
HONEYCOMB_DATASET=otel-python
```

Get a Honeycomb API Key from your Team Settings in [Honeycomb](https://ui.honeycomb.io).
(find this by clicking on your profile in the lower-left corner.)

You can name the Honeycomb Dataset anything you want.

You can choose any Service Name you want.

#### See the results

Run the app. 

`python3 server.py`

Hit it at http://localhost:5000

Activate the sequence of numbers.
Go to [Honeycomb](https://ui.honeycomb.io) and choose the Dataset you configured.

NOTE: You can see the full URL for the request in `http.target` 
(the examples in other languages often use `http.url`)

How many traces are there?

How many spans are in the traces?

Why are there so many??

Which trace has the most, and why is it different?

## 2. Customize a span

Let's make it easier to see what the "index" query parameter is.

To do this, change the code using the OpenTelemetry API.

Add this inside `server.py`'s `fibHandler()` function:

```
    current_span = trace.get_current_span()
    current_span.set_attribute("parameter.index", i)
```

(This requires the import `from opentelemetry import trace`)

Restart the app, make the sequence go, and find that field on the new spans.

Can you make the trace waterfall view show the index? What pattern does it show?

## 3. Create a custom span

Make the calculation into its own span, to see how much of the time spent on
this service is the meat: adding the fibonacci numbers.

To do this, put a calculation into a `with` block that creates its own span:

```python
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("calculate") as span:
          returnValue = int(respOne.content) + int(respTwo.content)
          span.set_attribute("result", returnValue)
```

After a restart, do your traces show this extra span? Do you see the name of your method?
About what fraction of the service time is spend in it?


## How does this work?

This app uses the OpenTelemetry autoinstrumentation python and flask.

This app is set up to magically notice incoming and outgoing HTTP requests,
and send these to Honeycomb (once you configure the env variables).
See the setup in `tracing.py`. There's code to initialize the TracerProvider,
and then there's this magic to create traces and spans where you're likely to want them:

```
# auto-instrument incoming requests
FlaskInstrumentor().instrument_app(app)
# auto-instrument outgoing requests
RequestsInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())
```

Also notice the libraries imported in `requirements.txt`. 
For details, [OpenTelemetry docs are here](https://opentelemetry-python.readthedocs.io/en/stable/)
