# environment
import os
from dotenv import load_dotenv

# import application factory
from api import create_app

# load environment variables
load_dotenv()
# get environment
environment = os.environ.get("ENVIRONMENT")
# check environment
if environment is None:
    # use development (default)
    environment = "development"
# create app with environment
app = create_app(environment=environment)

print(app)
# security headers
@app.after_request
def after_request_in(response):
    response.headers["strict-transport-security"] = "max-age=15552000"
    response.headers["Content-Security-Policy"] = 'frame-src "none"'
    response.headers["x-frame-options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Server"] = "pivony"
    return response


# run application
if __name__ == "__main__":
    app.run()
